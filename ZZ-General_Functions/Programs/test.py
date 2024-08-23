from sys import path


# Special Imports
path.append("YY_Notifications/Programs") 
from email_notification import email_alert

email_alert("Hello", "This is a simple test", "aces.cryptotrading@gmail.com")