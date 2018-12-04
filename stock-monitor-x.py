import requests
import smtplib
import os
from bs4 import BeautifulSoup
from email.message import EmailMessage

WORK_DIR = os.path.dirname(os.path.realpath(__file__))
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('user@gmail.com', 'xxxxxxxx')


def send_mail(subject):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'user@gmail.com'
    msg['To'] = 'receiver@gmail.com'
    server.send_message(msg)


def scrape_page(url):
    res = requests.get(
        'http://localhost:8050/render.html?url={}&timeout=60&wait=10'.format(url))
    page = res.content
    if len(page) >= 100000:
        return page
    else:
        scrape_page(url)

hose_page = scrape_page("http://priceboard.fpts.com.vn/?s=34%26t=aAll")
hnx_page = scrape_page("http://priceboard.fpts.com.vn/?s=34%26t=aHNXIndex")
upcom_page = scrape_page("http://priceboard.fpts.com.vn/?s=34%26t=aHNXUpcomIndex")

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
        send_mail(line + " reached! " + stock_code + "=" + figure)
        out_lines.append(line + " and False")
        is_changed = True
    else:
        out_lines.append(line)

if is_changed:
    with open(file_path, 'w') as f:
        for item in out_lines:
            f.write("%s\n" % item)