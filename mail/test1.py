#!/usr/bin/python

import smtplib

sender = 'qi.sun@cybex.io'
receivers = ['qi.sun@cybex.io']

message = """From: From Person <from@fromdomain.com>
To: To Person <to@todomain.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""

try:
   smtpObj = smtplib.SMTP(host = '127.0.0.1',  timeout = 26)
   smtpObj.sendmail(sender, receivers, message)         
   print "Successfully sent email"
except smtplib.SMTPException:
   print "Error: unable to send email"
