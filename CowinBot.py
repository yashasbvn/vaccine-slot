import smtplib, ssl
import requests
import json
import pandas as pd
from getpass import getpass
import datetime
import time
import string
from pandas.io.json import json_normalize #package for flattening json in pandas df
import base64
import csv
import np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

headers = {
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
}
tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
tomorrow_date = tomorrow_date.strftime("%d-%m-%Y")
today_date = datetime.date.today()
today_date = today_date.strftime("%d-%m-%Y")
time_now = time.localtime()
current_time = time.strftime("%H:%M:%S", time_now)

url_urban = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=265&date="+tomorrow_date
url_bbmp = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=294&date="+tomorrow_date
url_dummy = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=190015&date=23-05-2021"


r= requests.get(url = url_urban, headers = headers)
content1 = r.content
#print(r.content)
content = content1.decode("utf-8")
content = json.dumps(content)

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = ""  # Enter your address
receiver_email = ['example@email.com']  # Enter receiver address
password = "" #getpass("Please type your password:")
message = str(content)

open('session.json', 'w').close()
text_file = open("session.json", "w")
n = text_file.write(str(content1)[1:].replace("'",""))
text_file.close()
#print(len(message))

with open('session.json') as f:
    d = json.load(f)

#lets put the data into a pandas df
#clicking on session.json under "Input Files"
#tells us parent node is 'sessions'
slot_availabilty = json_normalize(d['sessions'])
slot_availabilty_18 = slot_availabilty.query('available_capacity_dose1 > 0 & min_age_limit == 18')
slot_availabilty_18.to_csv('slot_availabilty.csv', index=False)
np.savetxt('slot_availabilty.txt', slot_availabilty_18['name'], fmt='%s', delimiter=';')
dose1_available = slot_availabilty_18['available_capacity_dose1'].sum()
print('Total Dose 1 Available slots: '+str(dose1_available))


filename = "slot_availabilty.txt"
fo = open(filename, "rb")
filecontent = fo.read()
encodedcontent = base64.b64encode(filecontent)
marker = "AUNIQUEMARKER"

body ="""
SLOTS AVAILABLE FOR TOMORROW!!!
"""
# Define the main headers.
part1 = """From: Vaccination Bot by Yashas <me@fromdomain.net>
To: You <example@email.com>
Subject: VACCINATION SLOTS AVAILABLE - BENGALURU URBAN
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=%s
--%s
""" % (marker, marker)

# Define the message action
part2 = """Content-Type: text/plain
Content-Transfer-Encoding:8bit

%s
--%s
""" % (body,marker)

# Define the attachment section
part3 = """Content-Type: multipart/mixed; name=\"%s\"
Content-Transfer-Encoding:base64
Content-Disposition: attachment; filename=%s

%s
--%s--
""" %(filename, filename, filecontent, marker)
message = part1 + part2 + part3

email = 'Total Dose 1 Available slots: '+str(dose1_available)

if len(message) == 19 or slot_availabilty_18['available_capacity_dose1'].sum() <= 20 : #
	print('No Slots Available at '+current_time+ ' in BENGALURU URBAN district')
else:
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message)
		server.quit()
