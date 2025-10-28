"""
Example InterFAX send (demo). Replace with provider of choice and store credentials in Secrets Manager.
"""
import requests
import os

INTERFAX_USER = os.environ.get("INTERFAX_USER")
INTERFAX_PASS = os.environ.get("INTERFAX_PASS")
INTERFAX_API = "https://api.interfax.net/outbound/faxes"

def send_fax_via_interfax(fax_number, pdf_bytes, cover_text="MADO report"):
    files = {
        'file': ('mado.pdf', pdf_bytes, 'application/pdf'),
        'faxNumber': (None, fax_number),
        'coverText': (None, cover_text)
    }
    resp = requests.post(INTERFAX_API, auth=(INTERFAX_USER, INTERFAX_PASS), files=files)
    resp.raise_for_status()
    return resp.json()