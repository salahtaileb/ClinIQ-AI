"""
Fill an AcroForm MADO PDF using pdfrw.

Requires:
  pip install pdfrw

Usage:
  from fill_mado_pdf import fill_pdf_bytes
  data = { 'nom_prenoms_patient': 'Jean Dupont', 'date_de_naissance': '1980-01-01', ... }
  pdf_bytes = fill_pdf_bytes('mado_form.pdf', field_map, data)
  # save or attach pdf_bytes to email/fax
"""

from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName
import io

def _set_pdf_field(obj, key, value):
    if value is None:
        return
    obj.update({PdfName("/V"): value})
    if obj.get("/FT") == PdfName("/Btn") and isinstance(value, bool):
        obj.update({PdfName("/AS"): PdfName("Yes") if value else PdfName("Off")})

def fill_pdf_bytes(template_path, field_map, data_dict, flatten=True):
    pdf = PdfReader(template_path)
    if not pdf.Root or not pdf.Root.AcroForm:
        raise RuntimeError("PDF has no AcroForm; may be XFA or not a fillable form.")

    fields = pdf.Root.AcroForm.get("/Fields", [])
    for f in fields:
        f_obj = f.resolve()
        pdf_name = f_obj.get("/T")
        if pdf_name:
            pdf_name_str = str(pdf_name).strip()
            for canon_key, mapped_pdf_name in field_map.items():
                if mapped_pdf_name == pdf_name_str:
                    value = data_dict.get(canon_key)
                    _set_pdf_field(f_obj, PdfName("/V"), value if value is not None else "")
    pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfDict(True)))
    out_io = io.BytesIO()
    PdfWriter(out_io, trailer=pdf).write()
    out_bytes = out_io.getvalue()
    if flatten:
        pass
    return out_bytes
