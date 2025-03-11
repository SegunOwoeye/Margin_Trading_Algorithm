import smtplib
from email.message import EmailMessage

def email_alert(subject, body, to):
    user = "aces.cryptotrading@gmail.com"
    password = ""

    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    msg['from'] = user

    user = "aces.cryptotrading@gmail.com"
    password = ""

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()

# Test

#email_alert("Hello", "This is a simple test", "johndoe@icloud.com")

