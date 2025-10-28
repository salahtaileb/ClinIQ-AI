"""
Download the PDF form and list interactive form field names and types.

Usage:
  python list_pdf_fields.py https://example.org/AS-770_DT9070%20(2024-06)%20D.pdf

This script uses `pdfrw` to read AcroForm fields and prints their names.
Install: pip install pdfrw requests
"""
import sys
import requests
from pdfrw import PdfReader, PdfDict

def download_pdf(url, out_path="mado_form.pdf"):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path

def list_fields(pdf_path):
    pdf = PdfReader(pdf_path)
    fields = []
    if pdf.Root and pdf.Root.AcroForm:
        form = pdf.Root.AcroForm
        raw_fields = form.get("/Fields", [])
        for f in raw_fields:
            f_obj = f.resolve()
            name = f_obj.get("/T")
            ftype = f_obj.get("/FT")
            fields.append((str(name) if name else None, str(ftype) if ftype else None))
    return fields

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python list_pdf_fields.py <pdf_url>")
        sys.exit(1)
    url = sys.argv[1]
    pdf_path = download_pdf(url, out_path="mado_form.pdf")
    print(f"Saved PDF to {pdf_path}")
    fields = list_fields(pdf_path)
    if not fields:
        print("No AcroForm fields found or PDF uses XFA. See notes below.")
    for name, ftype in fields:
        print(f"FIELD: name={name} type={ftype}")

    # Note: If the PDF uses XFA forms, pdfrw won't list them. Use `pdfminer`, `pdfplumber`,
    # or inspect the PDF in Acrobat to get XFA field names or convert to AcroForm.