# MADO feature - setup and testing

This document describes the steps to finish setup and test the MADO generate/send workflow (feature/mado-agent branch).

Prerequisites
- AWS account with:
  - Secrets Manager access (to create `cliniq/mado/interfax` secret)
  - S3 bucket `aurascribe` (or set S3_BUCKET env var to your bucket)
  - KMS CMK for SSE-KMS (recommended alias: `alias/cliniq-mado`)
- InterFAX credentials (sandbox or production)
- AS-770 PDF file (place at `backend/mado/mado_form.pdf`) or ensure the field mapping exists

Create InterFAX secret (example CLI)

```
aws secretsmanager create-secret \
  --name cliniq/mado/interfax \
  --description "InterFAX creds for MADO sends" \
  --secret-string '{"INTERFAX_USER":"your_user","INTERFAX_PASS":"your_pass"}' \
  --region ca-central-1
```

Field mapping
1. Install dependencies for the field-list script: `pip install pdfrw requests`
2. Run the field-list script to enumerate PDF fields:

```
python backend/mado/list_pdf_fields.py "<AS-770 PDF URL>"
```

3. Create `data/mado_pdf_field_map.json` mapping PDF field names to canonical keys (or use the CSV template in `data/mado_pdf_field_map_template.csv`).

Running locally (dev)
1. Backend
- Ensure AWS credentials/profile with PutObject/GetObject on `aurascribe` exist.
- Set env vars:
  - AWS_REGION=ca-central-1
  - S3_BUCKET=aurascribe
  - (optional) KMS_KEY_ALIAS=alias/cliniq-mado
- Start backend (example using uvicorn):
```
uvicorn backend.app.main:app --reload --port 8000
```

2. Frontend
- cd frontend
- npm install
- npm run dev
- Open the app and go to the MADO Drafts demo page

Testing flow
1. Generate a draft via the UI or curl (see README earlier). The response includes a preview_url for the filled PDF.
2. Use Download / Print to manually fax to the region's télécopieur.
3. When `cliniq/mado/interfax` secret exists and app has access, using Send Fax will call InterFAX and return a provider job id; the draft metadata in S3 will be updated with send status and provider_job_id.

Security and compliance notes
- MADO reports contain PHI. Require clinician sign-off before sending and store only approved PDFs in S3 with SSE-KMS.
- Do NOT commit secrets to the repository. Use AWS Secrets Manager for InterFAX credentials.
