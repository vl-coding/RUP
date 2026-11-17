import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

## Email details
# sender_email = "desk-exam@rutgersuniversitypress.org"


# cc_recipients = "desk-exam@rutgersuniversitypress.org"
sender_email = os.getenv("GMAIL_ADDRESS")
password = os.getenv("GMAIL_APP_PASSWORD")
recipients = os.getenv("GMAIL_ADDRESS")
cc_recipients = os.getenv("GMAIL_ADDRESS")

subject = "Your Subject Line"
body = "This is the body of the email."

## Create the email
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = recipients
message["Cc"] = cc_recipients
message["Subject"] = subject

## Attach the email body
message.attach(MIMEText(body, "plain"))

## Combine all recipients (to + cc)
all_recipients = recipients, cc_recipients

## Connect to the SMTP server and send the email
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, password)
        server.sendmail(sender_email, all_recipients, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {e}")