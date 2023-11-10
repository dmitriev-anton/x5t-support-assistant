
def send_sms(phone_num, text):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    sms_text = "Добрый день. " \
               "{0}" \
               " С уважением, группа поддержки сервисов транспорта"
    postfix = '@sms.beeline.amega-inform.ru'
    link = "beeline.amega-inform.ru"
    login = "316801.1"
    password = "SupportX5T2023"
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
    server = smtplib.SMTP(host='beeline.amega-inform.ru',port=256)
    server.starttls()

    # Login Credentials for sending the mail
    server.login(login, password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

phone_num = '9127609251'

#send_sms(phone_num, 'СМС работает!')

#print("successfully sent email to %s:" % (phone_num))