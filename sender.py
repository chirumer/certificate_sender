# modules
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from getpass import getpass
from io import BytesIO
from time import sleep

# constants
smtp_url = 'smtp.zoho.in'
smtp_port = 587 # TLS
my_email = 'admin@cryptonger.com'
my_password = getpass()

template_path = 'certificate_template.png'
template_extension = 'png'
recipients_path = 'recipients.txt'

# script
def main():
    # get certificate template
    certificate_template = Image.open(template_path)

    # get recipients list
    data = open(recipients_path)
    recipients = []
    for line in data:
        email, name = map(str.strip, line.split('\t'))
        recipients.append({'name':name, 'email':email})

    # start smtp
    server = SMTP(smtp_url, smtp_port)
    server.starttls()
    server.login(my_email, my_password)

    # send emails
    for index, recipient in enumerate(recipients):
        try:
            print(index, 'sending email', recipient['email'])
            send_mail(server, recipient, certificate_template)
            print('email sent')
        except Exception as e:
            print('error')
            print(e)
            input()
        sleep(60) # 1 min 
    
    server.quit()

# helper functions
def send_mail(server, recipient, certificate_template):
    mail_body = (
        f'{recipient["name"]},\n'
        'Thanks for attending the cryptonger events.\n'
        'A proficiency certificate is attached.'
    )
    mail_subject = 'Proficiency certificate'

    # generate the certificate
    certificate_img = create_certificate(
        certificate_template.copy(),
        recipient['name']
    )
    certificate_stream = BytesIO()
    certificate_img.save(certificate_stream, format=template_extension)
    certificate_stream.seek(0)
    certificate = certificate_stream.read()

    # build the email
    mail = MIMEMultipart()
    mail['Subject'] = mail_subject
    mail['From'] = my_email
    mail['To'] = recipient['email']

    mail.attach(MIMEText(mail_body)) # mail body
    mail.attach(
        MIMEImage(certificate, name=f'certificate.{template_extension}')
    ) 
        # certificate image

    # send the email
    server.sendmail(my_email, recipient['email'], mail.as_string())

def create_certificate(certificate, name):
    # boundaries for the name
    start_x = 407
    end_x = 959
    centre_x = (start_x + end_x)/2
    bottom_y = 308
    
    # get ready to insert name
    draw = ImageDraw.Draw(certificate)
    font = ImageFont.truetype('caslon.ttf', 40)
    name_width, name_height = get_dimensions(name, font)

    # coordinates for name to be inserted
    x = centre_x - name_width/2
    y = bottom_y - name_height

    # insert name
    draw.text((x, y), name, (0, 0, 0), font=font)
    
    return certificate

def get_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

if __name__ == '__main__':
    main()
