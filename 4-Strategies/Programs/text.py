import os
from sys import path
from Trade_Order_Planning import pair_balance, calculating_markers

text = os.getcwd()
print(text)
path.append("YY_Notifications/Programs")
from email_notification import email_alert
text = os.getcwd()
print(text)