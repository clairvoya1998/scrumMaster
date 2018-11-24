import email
import imaplib

EMAIL_PROVIDER   = "@gmail.com"
EMAIL_ADDRESS  = "alexa.scrum.master" + EMAIL_PROVIDER
EMAIL_PASSWORD    = "alexa2018!"
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT   = 993

def readmail():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, port=IMAP_PORT)

    try:
        rv, data = mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    except:
        print("LOGIN FAILED!!!")
        sys.exit(1)
    print("Logged in")

    mail.select('inbox', readonly=1)
    result, data = mail.search(None, '(UNSEEN)')
    mail_ids = data[0]
    id_list = mail_ids.split()
    
    for i in id_list:
        result, data = mail.fetch(i, "(RFC822)")
        raw_email = data[0][1].decode("utf-8")
        #print(raw_email)

        email_message = email.message_from_string(raw_email)
        print(get_first_text_block(email_message))

def get_first_text_block(email_message_instance):
    maintype = email_message_instance.get_content_maintype()
    if maintype == 'multipart':
        for part in email_message_instance.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return email_message_instance.get_payload()



    # first_email_id = int(id_list[0])
    # latest_email_id = int(id_list[-1])
    #
    # print("Before loop")
    # for i in range(latest_email_id, first_email_id, -1):
    #     print("In loop")
    #     typ, data = mail.fetch(i, '(RFC822)' )
    #
    #     for response_part in messages:
    #         if isinstance(response_part, tuple):
    #             msg = email.message_from_string(response_part[1])
    #             email_subject = msg['subject']
    #             email_from = msg['from']
    #             print('From : ' + email_from + '\n')
    #             print('Subject : ' + email_subject + '\n')

readmail()
