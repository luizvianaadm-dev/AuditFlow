import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.sender_email = os.getenv("SMTP_SENDER", self.smtp_user)

    def send_email(self, to_email: str, subject: str, body: str, attachments: list = None):
        """
        Sends an email with optional attachments.
        Attachments should be a list of dicts: {'filename': 'name.ext', 'content': bytes} or paths.
        """
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        if attachments:
            for attach in attachments:
                if isinstance(attach, dict) and 'content' in attach:
                    part = MIMEApplication(attach['content'], Name=attach['filename'])
                elif isinstance(attach, str) and os.path.exists(attach):
                    with open(attach, "rb") as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(attach))
                else:
                    continue # Skip invalid attachment
                
                part['Content-Disposition'] = f'attachment; filename="{attach.get("filename", "attachment") if isinstance(attach, dict) else os.path.basename(attach)}"'
                msg.attach(part)

        try:
            # For development, just log if credentials missing
            if not self.smtp_user:
                print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}")
                return True

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

email_service = EmailService()
