
import requests
from bs4 import BeautifulSoup
import smtplib
from config import EMAIL, PASSWORD
import time
import mysql.connector

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
    def __init__(self, url, headers):
        super().__init__(url, headers)
        self.connect_to_db()
        self.last_price = None
        
    def connect_to_db(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bazos")
        self.cursor = self.connection.cursor()
        
    def check_existing(self, title, price):
        query = "SELECT * FROM listings WHERE title = %s AND price = %s"
        self.cursor.execute(query, (title, price))
        return self.cursor.fetchone() is not None
    
        
    def store_in_db(self, title, price):
        if not self.check_existing(title, price):
            query = "INSERT INTO listings (title, price) VALUES (%s, %s)"
            values = (title, price)
            self.cursor.execute(query, values)
            self.connection.commit()
        else:
            print("The listing with the same title and price already exists. Not saving.")

    
    def extrakt_data(self, page):
        soup = BeautifulSoup(page.content, 'html.parser')

        # title = soup.find(class_="nadpisdetail").get_text()
        title_element = soup.find(class_="nadpisdetail")
        if title_element:
            title = title_element.get_text()
        else:
            print("Title element was not found on the page!")
            return


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
        self.store_in_db(title, converted_price)

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
URL = 'https://reality.bazos.sk/inzerat/154590455/2-izbovy-byt-sidliii-presov-aj-na-splatky-bez-hypoteky.php'
scraper = BazosScraper(URL, my_headers)

scraper.start()

# while(True):
#     scraper.start()
#     time.sleep(60 * 60)
    