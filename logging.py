"""
Created by Mariusz on 29/04/29
Program logs how long machine is operating using interrupts (detecting edges).

Once weekly on the selected day and time generates report and send it via email. It also does it monthly.
Reports are recorded and generated using Pandas.

"""

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print('Error Importing RPI.GPIO, Check if package installed or run application with "sudo"')

import time
import datetime
import pandas as pd
import os, glob
import urllib

import smtplib, email, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Global variables to be shared with interrupts
startTime = 0
stopTime = 0
trigger_rising = False
trigger_falling = False
PATH = '/home/pi/Logs'
DAY_OF_WEEK = 'Wed'
DAY_OF_MONTH = '01'
TIME = '15:39'
HEADER = ['start time','stop time']
SENDER_EMAIL = ''
RECEIVER_EMAIL = ''
PASSWORD = ''
def edge_callback(channel):
    """
    Interrupt Handler on GPIO22
    Record start time on rising edge and stop time on falling edge.
    Set trigger to pass it to program
    """
    global startTime, stopTime,trigger_rising, trigger_falling
    
    if GPIO.input(22) == GPIO.HIGH :
        startTime = datetime.datetime.now()
        trigger_rising = True
        print ("rising Edge detected")
    elif GPIO.input(22) == GPIO.LOW:
        stopTime = datetime.datetime.now()
        trigger_falling = True
        print ("falling Edge detected")
        

def check_connection():
    """
    Return True if connected to internet or False if connections is down
    """
    try:
        url = "https://www.google.com"
        urllib.request.urlopen(url)
        status = "Connected"
    except:
        status = "Not Connected"
        
    if status == "Connected":
        return True
    else:
        return False

def record_time(recorded_time, edge = False):
    """
    Input: time to record and edge, False - Rising, True - Falling.
    Output: None
    """
    # check if Logs directory exists, if not create it
    path = PATH
    file = 'log.csv'
    
    if os.path.exists(path) == False:
        try:
            os.mkdir(path)
        except OSError:
            print ('creating of "Logs" directory failed')
        else:
            print ('"Logs" directory created')
     
    # if log file exists in 'Logs' directory
    if os.path.isfile(path +'/' + file):
        df = pd.read_csv(path + '/' + file, usecols=HEADER)

    else:
        # create empty DataFrame
        df = pd.DataFrame(columns=HEADER)

    if edge == False:
        print (df)
        df1 = pd.DataFrame([recorded_time], columns = [HEADER[0]]) 
        df = pd.concat([df,df1], axis=0, sort=False)
                
    if edge == True:
        
        df.at[0 if pd.isnull(df.index.max()) else df.index.max(), HEADER[1]] = recorded_time
    
    df.to_csv(path + '/' + file)

def generate_report(path, file, log, date, report_type = False):
    """
    Input: path and file, report_type default false - weekly, True - monthly. date of a report.
    Return DataFrame
    """

    if os.path.isfile(path +'/' + log):
        df = pd.read_csv(path + '/' + log, usecols=HEADER, parse_dates=HEADER, date_parser=pd.to_datetime)
        df['duration'] = df[HEADER[1]] - df[HEADER[0]]
    else:
        print ('file doesnt exist')
        return None
    
    endDate = date
    if report_type:
        yesterday = endDate - datetime.timedelta(days = 2)
        yesterday = yesterday.replace(day = 1)
        startDate = yesterday - datetime.timedelta (days = 1)
    else:
        startDate = date - datetime.timedelta (days = 7)
    
    # Drop all the No numbers
    df = df.dropna()
    
    # filter data
    data = df[(df[HEADER[1]] <= endDate) & (df[HEADER[1]] >= startDate)]
    
    # save report
    df.to_csv(path + '/' + file, date_format='%d-%m-%Y %H:%M:%S')
    
    # calculate total
    total = data['duration'].sum()
    
    # get seconds of the total
    total = total.total_seconds()
    
    # return data and operating hours
    return (data, "{:.2f} operating hours".format(total/3600))
    
def email_send(path, file, emailOut, emailPassword, emailIn, email_body):
    """
    Input: takes path and file to send, sender email and password and email receipient
    Function sends email
    """
    subject = "Email with log " + file
    body = " This is automated email send with log " + file + email_body
    
    # create a multipart message and set headers
    message = MIMEMultipart()
    message['From'] = emailOut
    message['To'] = emailIn
    message['Subject'] = subject
    
    # add body to email
    message.attach(MIMEText(body,'plain'))
    
    filename = path +'/'+ file
    
    # Open file in binary mode
    with open(filename, 'rb') as attachment:
        part = MIMEBase('application','octet-stream')
        part.set_payload(attachment.read())
        
    # Encode file in ASCII to send via email
    encoders.encode_base64(part)
    
    # Add header as key/vlaue pair to attached part
    part.add_header("Content-Disposition",f"attachment; filename={file}",)
    
    # Add attachment to message and convert message to sting
    message.attach(part)
    text = message.as_string()
    
    # Log into server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(emailOut, emailPassword)
        server.sendmail(emailOut, emailIn, text)
           
# Set numbering pathern to be related to BCM    
GPIO.setmode(GPIO.BCM)

# Turn of warning display
GPIO.setwarnings(False)

# Set GPIO22 as Input
GPIO.setup(22,GPIO.IN)

# Set GPIO21 as Output
GPIO.setup(21,GPIO.OUT)

# Add interrupt event on GPIO22 for both edges
GPIO.add_event_detect(22, GPIO.BOTH,callback=edge_callback, bouncetime=300)

send_weekly_log = False
send_monthly_log = False
sending_weekly_in_progress = False
sending_monthly_in_progress = False

while ():
    # if rising edge detected 
    if trigger_rising == True:
        print (startTime)
        trigger_rising = False
        record_time(startTime)
    
    # if falling edge detected    
    if trigger_falling == True:
        print(stopTime)
        print(stopTime - startTime)
        trigger_falling = False
        record_time(stopTime, True)

    # Live LED set to High    
    GPIO.output(21,GPIO.HIGH)
    time.sleep(1)
    # Live LED set to Low
    GPIO.output(21,GPIO.LOW)
    time.sleep(1)
    
    # if it is Sunday and it is end of a day - 23:59
    if datetime.datetime.now().strftime("%a") == DAY_OF_WEEK and datetime.datetime.now().strftime("%H:%M") == TIME:      
        weekly_log = datetime.datetime.now().strftime("%d-%m-%Y") + '_Weekly.csv'
        # generate report only if doesn't exist
        if os.path.isfile(PATH +'/' + weekly_log) == False:
            weekly_report = generate_report(PATH, weekly_log, 'log.csv', datetime.datetime.now(), False)    
            send_weekly_log = True
    else:
        send_weekly_log = False
        
    # if it is first day of a month and it is end of a day - 23:59
    if datetime.datetime.now().strftime("%d") == DAY_OF_MONTH and datetime.datetime.now().strftime("%H:%M") == TIME:
        monthly_log = datetime.datetime.now().strftime("%d-%m-%Y") + '_Monthly.csv'        
        # generate report only if doesn't exist
        if os.path.isfile(PATH +'/' + monthly_log) == False:
            monthly_report = generate_report(PATH, monthly_log, 'log.csv', datetime.datetime.now(), True)    
            send_monthly_log = True
    else:
        send_monthly_log = False
        
    internet_connection = check_connection()
    
    # if weekly log need to be send check connection
    if send_weekly_log == True or sending_weekly_in_progress == True:
        if internet_connection:
            email_send(PATH,weekly_log, SENDER_EMAIL, PASSWORD, RECEIVER_EMAIL, ' for weekly usage total of ' + weekly_report[1])
            send_weekly_log = False
            sending_weekly_in_progress = False
        else:
            print ("no internet connection")
            sending_weekly_in_progress = True
            
    # if montly log need to be send check connection
    if send_monthly_log == True and sending_monthly_in_progress == False :
        if internet_connection:
            email_send(PATH,monthly_log, SENDER_EMAIL, PASSWORD, RECEIVER_EMAIL, ' for monthly usage total of ' + monthly_report[1])    
            send_monthly_log = False
            send_monthly_in_progress = False
        else:
            print ("no internet connection")
            sending_monthly_in_progress = True
