
def send_sms(phone_num, text):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    import os
    from dotenv import load_dotenv
    sms_text = "Добрый день. " \
               "{0}" \
               " С уважением, группа поддержки сервисов транспорта"
    postfix = '@sms.beeline.amega-inform.ru'
    load_dotenv()
    link = os.getenv("SMS_LINK")
    login = os.getenv("SMS_USERNAME")
    password = os.getenv("SMS_PASSWORD")
    sms_text = "Добрый день. " \
               "{0}" \
               " С уважением, группа поддержки сервисов транспорта"

    # create message object instance
    msg = MIMEMultipart()
    message = sms_text.format(text)

    # setup the parameters of the message

    msg['From'] = 'default@anything.tld'
    msg['To'] = phone_num+postfix
    msg['Subject'] = 'X5transport'

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    #create server
    server = smtplib.SMTP(host=link,port=256)
    server.starttls()

    # Login Credentials for sending the mail
    server.login(login, password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

#phone_num = '9127609251'

#send_sms(phone_num, 'СМС работает!')

#print("successfully sent email to %s:" % (phone_num))