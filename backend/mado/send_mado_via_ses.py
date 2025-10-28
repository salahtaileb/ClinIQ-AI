"""
Send the filled MADO PDF via AWS SES and return message-id.

Requires:
  pip install boto3
  AWS credentials available via environment or IAM role.
"""
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import datetime

SES_REGION = "ca-central-1"
SENDER = "clinic@example.org"

def send_mado_email(recipient_email, subject, body_text, pdf_bytes, pdf_filename="MADO_filled.pdf"):
    ses = boto3.client("ses", region_name=SES_REGION)
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = recipient_email

    part = MIMEText(body_text, "plain", "utf-8")
    msg.attach(part)

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header("Content-Disposition", "attachment", filename=pdf_filename)
    msg.attach(attachment)

    raw_bytes = msg.as_string().encode("utf-8")
    resp = ses.send_raw_email(RawMessage={"Data": raw_bytes}, Source=SENDER, Destinations=[recipient_email])
    message_id = resp.get("MessageId")
    return message_id
