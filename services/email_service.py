# services/email_service.py

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    def __init__(self):
        self.host = os.getenv("EMAIL_HOST")
        self.port = int(os.getenv("EMAIL_PORT", 587))
        self.user = os.getenv("EMAIL_HOST_USER")
        self.password = os.getenv("EMAIL_HOST_PASSWORD")
        self.sender_name = os.getenv("EMAIL_SENDER_NAME")

        if not all([self.host, self.port, self.user, self.password, self.sender_name]):
            raise ValueError("Email configuration is missing from environment variables.")

    def send_emails(self, recipients: list[str], subject: str, html_body_template: str, data: list[dict]):
        sent_count = 0
        email_field_candidates = ['email', 'Email', 'customer_email']

        # Determine the email field from the data
        email_field = None
        if data:
            for field in email_field_candidates:
                if field in data[0]:
                    email_field = field
                    break

        if not email_field:
            raise ValueError("Could not find a valid email field in the query result data.")

        to_addresses = [row[email_field] for row in data if email_field in row and row[email_field]]

        if not to_addresses:
            return "No valid recipient email addresses found in the data."

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)

                for row_data in data:
                    recipient_email = row_data.get(email_field)
                    if not recipient_email:
                        continue

                    msg = MIMEMultipart('alternative')
                    msg['From'] = f"{self.sender_name} <{self.user}>"
                    msg['To'] = recipient_email
                    msg['Subject'] = subject

                    # Personalize content
                    html_body = html_body_template
                    for key, value in row_data.items():
                        html_body = html_body.replace(f"{{{{{key}}}}}", str(value))

                    msg.attach(MIMEText(html_body, 'html'))
                    server.sendmail(self.user, recipient_email, msg.as_string())
                    sent_count += 1

            return f"Emails sent successfully to {sent_count} users."

        except Exception as e:
            raise RuntimeError(f"Failed to send emails: {e}")


email_service = EmailService()