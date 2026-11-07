import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

## Email details
email = {'to': 'recipient@example.com', 'cc': 'desk-exam@rutgersuniversitypress.org', 'subject line': 'Exam Copy Request', 'content': 'Dear Professor,\n\nThank you for your exam copy request for this title.\u202f Below is a discount code that you can use in our shopping cart to buy the exam copy at $15.00 (free shipping) and a link to an electronic exam copy for your use.\n\n<DISCOUNT_CODE>\n\n<EXAM_COPY_LINK>\n'}

def send_email(content):
    password = os.getenv("OUTLOOK_APP_PASSWORD") # make app password somehow

    ## Create the email
    message = MIMEMultipart()
    message["From"] = "desk-exam@rutgersuniversitypress.org"
    message["To"] = email["to"]
    message["Cc"] = "desk-exam@rutgersuniversitypress.org"
    message["Subject"] = email["subject line"]

    ## Attach the email body
    message.attach(MIMEText(f"<i>{email['content']}</i>", 'html'))

    ## Combine all recipients (to + cc)
    all_recipients = email["to"], email["cc"]

    ## Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login("desk-exam@rutgersuniversitypress.org", password)
            server.sendmail("desk-exam@rutgersuniversitypress.org", all_recipients, message.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
# print( send_email(email) )