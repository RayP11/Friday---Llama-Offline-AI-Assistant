import smtplib
import os
from dotenv import load_dotenv
import ssl
from email.message import EmailMessage

load_dotenv()

email_sender = os.getenv("EMAIL_SENDER")
email_password = os.getenv("EMAIL_PASSWORD")
email_receiver = os.getenv("MY_NUMBER") #personal phone number
soph_number = os.getenv("SOPHIE_NUMBER") #girlfriend phone number

def send_reminder(message):
    """Message reminders sent to myself"""
    body = message

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    print(message + " was sent")

def send_message(message):
    """Message to be sent to other people (Sophie in this case)"""
    body = message

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = soph_number
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, soph_number, em.as_string())
    print(message + " was sent")