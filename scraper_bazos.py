import requests
from bs4 import BeautifulSoup
import smtplib
from config import EMAIL, PASSWORD
import time


URL = 'https://reality.bazos.sk/inzerat/154307277/2-izbovy-byt-sidliii-presov-aj-na-splatky-bez-hypoteky.php'

my_headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

last_price = None

def check_price():
    global last_price
    
    page = requests.get(URL, headers=my_headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # print(soup.prettify())

    title = soup.find(class_="nadpisdetail").get_text()
    # price = soup.find(id="" or class_="").get_text()
    # converted_price = float(price[0:5]) - not realy for me
    # print(converted_price)
    if not title:
        send_mail("Listing Not Found", "The listing on the bazos.sk website was not found.")
        return
    # print(title.strip())

    price_string = soup.find(string="Cena:")
    
    if not price_string:
        send_mail("Price Not Found", "The listing price on Bazos.sk was not found.")
        return

    price_element = price_string.find_next('b')
    price = price_element.get_text().strip()
    converted_price = float(price.replace("€", "").replace(" ", "").replace(",", "."))

    if last_price is None:
        send_mail("Listing Found", f"The listing has a current price of {price}.")
    if last_price != converted_price:
        if last_price < converted_price:
            send_mail("Price Increased", f"The listing price increased from {last_price}€ to {converted_price}€.")
        else:
            send_mail("Price Decreased", f"The listing price decreased from {last_price}€ to {converted_price}€.")        
    else:
        print("Price Unchanged", f"The listing price remains the same at {converted_price} as before.")
    
    last_price = converted_price
    
def send_mail(subject, body):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(EMAIL, PASSWORD)

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(EMAIL, EMAIL, msg)

    print(f'Email sent with subject: {subject}')

    server.quit()

# check_price()

while(True):
    check_price()
    time.sleep(60 * 60)
    