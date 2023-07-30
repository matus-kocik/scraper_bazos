import requests
from bs4 import BeautifulSoup
import smtplib
from config import EMAIL, PASSWORD


URL = 'https://reality.bazos.sk/inzerat/153724690/2-izbovy-svetly-byt-v-tichej-lokalite-ul-karpatska-sekcov.php'

my_headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

def check_price():
    page = requests.get(URL, headers=my_headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    # print(soup.prettify())

    title = soup.find(class_="nadpisdetail").get_text()
    # price = soup.find(id="" or class_="").get_text()
    # converted_price = float(price[0:5]) - not realy for me
    # print(converted_price)

    print(title.strip())

    price_string = soup.find(string="Cena:")

    if price_string:
        price_element = price_string.find_next('b')
        price = price_element.get_text().strip()
    else:
        print("Price not found on the website.")

    converted_price = float(price.replace("€", "").replace(" ", "").replace(",", "."))

    if (converted_price > 99991):
        send_mail()
    else:
        print("Price is not change!")
        
def send_mail():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    
    server.login(EMAIL, PASSWORD)
    
    subject = 'Price fell down!'
    
    body = 'Check the bazos! Link: https://reality.bazos.sk/inzerat/153724690/2-izbovy-svetly-byt-v-tichej-lokalite-ul-karpatska-sekcov.php'
    
    msg = f"Subject: {subject}\n\n{body}"