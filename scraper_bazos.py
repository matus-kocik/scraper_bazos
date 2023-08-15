
import requests
from bs4 import BeautifulSoup
import smtplib
from config import EMAIL, PASSWORD
import time

class Scraper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.last_price = None
        
    def load_data(self):
        return requests.get(self.url, headers = self.headers)

    def extrakt_data(self, page):
        raise NotImplementedError
    
    def start(self):
        page = self.load_data()
        self.extrakt_data(page)

class BazosScraper(Scraper):
    def extrakt_data(self, page):
        soup = BeautifulSoup(page.content, 'html.parser')

        title = soup.find(class_="nadpisdetail").get_text()

        if not title:
            self.send_mail("Listing Not Found", "The listing on the bazos.sk website was not found.")
            return
        
        price_string = soup.find(string="Cena:")
        if not price_string:
            self.send_mail("Price Not Found", "The listing price on Bazos.sk was not found.")
            return



        price_element = price_string.find_next('b')
        price = price_element.get_text().strip()
        converted_price = float(price.replace("€", "").replace(" ", "").replace(",", "."))

        if self.last_price is None:
            self.send_mail("Listing Found", f"{title} \n The listing has a current price of {price}.")
        if self.last_price is not None:
            if self.last_price != converted_price:
                if self.last_price < converted_price:
                    self.send_mail("Price Increased", f"{title} \n The listing price increased from {self.last_price}€ to {converted_price}€.")
                else:
                    self.send_mail("Price Decreased", f"{title} \n The listing price decreased from {self.last_price}€ to {converted_price}€.")        
            else:
                self.send_mail("Price Unchanged", f"{title} \n The listing price remains the same at {converted_price} as before.")
    
        self.last_price = converted_price
    
    def send_mail(self, subject, body):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL, PASSWORD)
        msg = f"Subject: {subject}\nContent-Type: text/plain; charset=UTF-8\n\n{body}"
        server.sendmail(EMAIL, EMAIL, msg.encode('utf-8'))
        print(f'Email was sent with the subject: {subject}')
        server.quit()
        
my_headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
URL = 'https://reality.bazos.sk/inzerat/154307277/2-izbovy-byt-sidliii-presov-aj-na-splatky-bez-hypoteky.php'
scraper = BazosScraper(URL, my_headers)


while(True):
    scraper.start()
    time.sleep(60 * 60)
    