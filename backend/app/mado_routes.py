from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import os
import boto3
import json
from datetime import datetime

from backend.mado.fill_mado_pdf import fill_pdf_bytes
from backend.mado.interfax_client import send_fax

router = APIRouter(prefix="/mado", tags=["mado"])

S3_BUCKET = os.environ.get("S3_BUCKET", "aurascribe")
KMS_KEY_ALIAS = os.environ.get("KMS_KEY_ALIAS", "alias/cliniq-mado")

secrets_client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION", "ca-central-1"))
s3_client = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "ca-central-1"))

class MadoGenerateRequest(BaseModel):
    encounter_id: str
    patient: dict
    extracted: dict
    region_id: Optional[str] = None

class MadoSendRequest(BaseModel):
    draft_id: str
    approve_by: str  # clinician user id
    transport: str  # 'fax' or 'manual'

def _get_interfax_creds(secret_name: str = "cliniq/mado/interfax"):
    try:
        resp = secrets_client.get_secret_value(SecretId=secret_name)
        secret_string = resp.get("SecretString")
        if not secret_string:
            return None
        data = json.loads(secret_string)
        return data.get("INTERFAX_USER"), data.get("INTERFAX_PASS")
    except Exception:
        return None


@router.post("/generate")
async def generate_mado(req: MadoGenerateRequest):
    # generate draft id
    draft_id = str(uuid.uuid4())

    # select region recipient - simple lookup if provided
    region_id = req.region_id or req.patient.get("region_id") or "06"

    # Map canonical fields -> PDF field mapping is expected in data/mado_pdf_field_map.json
    # For now assume field_map exists at that path and load it
    field_map = {}
    try:
        with open("data/mado_pdf_field_map.json", "r", encoding="utf-8") as f:
            field_map = json.load(f)
    except FileNotFoundError:
        # proceed with empty map; user must provide mapping
        pass

    # Prepare canonical data for MADO required fields
    canonical = {
        "nom_prenoms_patient": req.patient.get("name"),
        "date_de_naissance": req.patient.get("dob"),
        "adresse": req.patient.get("address"),
        "telephone": req.patient.get("phone"),
        "numero_assurance_maladie": req.patient.get("phn"),
        "nom_clinicien_declarant_et_coordonnees": req.extracted.get("clinician_name"),
        "nom_de_la_MADO": req.extracted.get("disease_name"),
        "date_declaration": datetime.utcnow().isoformat()
    }

    # fill PDF bytes; if the PDF mapping is missing this will raise
    try:
        pdf_bytes = fill_pdf_bytes("backend/mado/mado_form.pdf", field_map, canonical, flatten=False)
    except Exception as e:
        # return a helpful error so user can run list_pdf_fields
        raise HTTPException(status_code=500, detail=f"PDF fill failed: {e}")

    # store in S3 (draft)
    s3_key_pdf = f"mado/drafts/{draft_id}.pdf"
    s3_key_meta = f"mado/metadata/{draft_id}.json"
s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key_pdf, Body=pdf_bytes, ServerSideEncryption="aws:kms")

    metadata = {
        "id": draft_id,
        "encounter_id": req.encounter_id,
        "patient_hash": req.patient.get("phn") or req.patient.get("id"),
        "disease": req.extracted.get("disease_name"),
        "region_id": region_id,
        "recipient_fax": None,  # resolved below from recipients file
        "transport": "fax",
        "status": "draft",
        "s3_key": s3_key_pdf,
        "created_by": req.extracted.get("clinician_id") or "system",
        "created_at": datetime.utcnow().isoformat()
    }

    # resolve recipient fax from recipients JSON
    try:
        with open("data/mado_recipients.json","r",encoding="utf-8") as f:
            recipients = json.load(f)
            for r in recipients:
                if r.get("region_id") == region_id:
                    metadata["recipient_fax"] = r.get("fax_mado")
                    break
    except Exception:
        pass

    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key_meta, Body=json.dumps(metadata).encode("utf-8"), ServerSideEncryption="aws:kms")

    # generate presigned URL for preview (short lived)
    preview_url = s3_client.generate_presigned_url('get_object', Params={"Bucket": S3_BUCKET, "Key": s3_key_pdf}, ExpiresIn=3600)

    return {"draft_id": draft_id, "preview_url": preview_url, "metadata": metadata}


@router.post("/send")
async def send_mado(req: MadoSendRequest):
    # load metadata
    s3_key_meta = f"mado/metadata/{req.draft_id}.json"
    try:
        meta_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key_meta)
        meta = json.loads(meta_obj["Body"].read())
    except Exception:
        raise HTTPException(status_code=404, detail="draft not found")

    if req.transport == "manual":
        # mark as ready for manual print/fax
        meta["status"] = "manual_ready"
        meta["sent_at"] = None
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key_meta, Body=json.dumps(meta).encode("utf-8"), ServerSideEncryption="aws:kms")
        download_url = s3_client.generate_presigned_url('get_object', Params={"Bucket": S3_BUCKET, "Key": meta["s3_key"]}, ExpiresIn=3600)
        return {"draft_id": req.draft_id, "sent": False, "transport": "manual", "download_url": download_url}

    # transport == fax
    interfax_creds = _get_interfax_creds()
    if interfax_creds is None:
        raise HTTPException(status_code=500, detail="InterFAX credentials not available in Secrets Manager")
    interfax_user, interfax_pass = interfax_creds

    # download PDF bytes
    pdf_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=meta["s3_key"])['Body'].read()
    fax_number = meta.get("recipient_fax")
    if not fax_number:
        raise HTTPException(status_code=400, detail="recipient fax not configured for this region")

    try:
        resp = send_fax(interfax_user, interfax_pass, fax_number, pdf_obj, cover_text=f"MADO report: {meta.get('disease')}")
    except Exception as e:
        # record failure in metadata
        meta["status"] = "send_failed"
        meta["notes"] = str(e)
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key_meta, Body=json.dumps(meta).encode("utf-8"), ServerSideEncryption="aws:kms")
        raise HTTPException(status_code=502, detail=f"InterFAX send failed: {e}")

    # success: InterFAX returns job id; update meta and store
    job_id = resp.get("id") or resp.get("jobId") or resp.get("faxJobId") or str(uuid.uuid4())
    meta["status"] = "sent"
    meta["provider_job_id"] = job_id
    meta["sent_at"] = datetime.utcnow().isoformat()
    meta["sent_by"] = req.approve_by
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key_meta, Body=json.dumps(meta).encode("utf-8"), ServerSideEncryption="aws:kms")

    return {"draft_id": req.draft_id, "sent": True, "provider_job_id": job_id}