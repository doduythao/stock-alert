import configparser
import os
import requests
import smtplib
import sys

from bs4 import BeautifulSoup
from email.message import EmailMessage
from twilio.rest import Client

# 0 for WhatsApp | 1 for Email | 2 for Telegram
noti_method = int(sys.argv[2])

config = configparser.ConfigParser()
config.read(sys.argv[1])

# Your Account Sid and Auth Token from twilio.com/console for WhatsApp
account_sid = config['settings']['account_sid']
auth_token = config['settings']['auth_token']
whatsapp_from = config['settings']['whatsapp_from']
whatsapp_to = config['settings']['whatsapp_to']

sender_email = config['settings']['sender_email']
# sender pass is application password, not account password. (Google security)
sender_pass = config['settings']['sender_pass']
receiver_email = config['settings']['receiver_email']

# Telegram
bot_token = config['settings']['bot_token']
bot_chatID = config['settings']['bot_chatID']

WORK_DIR = os.path.dirname(os.path.realpath(__file__))

# prepare mail sender
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()


def send_mail(subject):
    server.login(sender_email, sender_pass)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    server.send_message(msg)


def send_whatsapp(message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=whatsapp_from,
        to=whatsapp_to
    )


def send_telegram(message):
    send_text = ('https://api.telegram.org/bot{0}'
                 '/sendMessage?chat_id={1}'
                 '&parse_mode=Markdown&text={2}').format(bot_token, bot_chatID, message)
    response = requests.get(send_text)
    return response.json()


def scrape_page(url):
    res = requests.get(
        'http://localhost:8050/render.html?url={}&timeout=60&wait=10'.format(url))
    page = res.content
    # if it too short, it means there are problem, retry
    if len(page) >= 100000:
        return page
    else:
        scrape_page(url)

hose_page = scrape_page("http://priceboard.fpts.com.vn/?s=34%26t=aAll")
hnx_page = scrape_page("http://priceboard.fpts.com.vn/?s=34%26t=aHNXIndex")
upcom_page = scrape_page(
    "http://priceboard.fpts.com.vn/?s=34%26t=aHNXUpcomIndex")

hose = BeautifulSoup(hose_page, 'html.parser')
hnx = BeautifulSoup(hnx_page, 'html.parser')
upcom = BeautifulSoup(upcom_page, 'html.parser')

print('Done BeautifulSoup')


def get_stock_price(code):
    css_selector = "tr[code='%s'] td:nth-of-type(12)" % code
    elem = hose.select(css_selector)
    if len(elem) > 0:
        return elem[0].text
    else:
        elem = hnx.select(css_selector)
        if len(elem) > 0:
            return elem[0].text
        else:
            elem = upcom.select(css_selector)
            if len(elem) > 0:
                return elem[0].text
            else:
                raise IndexError()


file_path = WORK_DIR + "/stock_list"
input_lines = tuple(open(file_path, 'r'))
out_lines = []
is_changed = False

for line in input_lines:
    line = line.strip()
    stock_code = line[0:3]
    figure = get_stock_price(stock_code)
    out_line = line.replace(stock_code, figure)
    if eval(out_line):
        message = line + " reached! " + stock_code + "=" + figure
        if noti_method == 0:
            send_whatsapp(message)
        elif noti_method == 1:
            send_mail(message)
        elif noti_method == 2:
            send_telegram(message)
        else:
            print('invalid noti_method!')
        out_lines.append(line + " and False")
        is_changed = True
    else:
        out_lines.append(line)

if is_changed:
    with open(file_path, 'w') as f:
        for item in out_lines:
            f.write("%s\n" % item)
