import requests
from bs4 import BeautifulSoup
import smtplib
from config import EMAIL, PASSWORD
import time
import mysql.connector
import logging

logging.basicConfig(filename='scraper_errors.log', level=logging.ERROR)


class Scraper:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.last_price = None
        
    def load_data(self):
        return requests.get(self.url, headers=self.headers)

    def extract_data(self, page):
        raise NotImplementedError
    
    def start(self):
        page = self.load_data()
        self.extract_data(page)

class BazosScraper(Scraper):
    def __init__(self, url, headers):
        super().__init__(url, headers)
        self.connect_to_db()
        self.last_price = self.fetch_last_price()
        
    def connect_to_db(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="bazos")
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            self.send_mail("Database Connection Error", f"Thera was an error connecting to the database: {err}")
                
    def fetch_last_price(self):
        query = "SELECT price FROM listings ORDER BY id DESC LIMIT 1"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result:
            return float(result[0])
        return None
        
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

    def extract_data(self, page):
        soup = BeautifulSoup(page.content, 'html.parser')

        title_element = soup.find(class_="nadpisdetail")
        if not title_element:
            print("Title element was not found on the page!")
            return
        title = title_element.get_text()

        price_string = soup.find(string="Cena:")
        if not price_string:
            self.send_mail("Price Not Found", "The listing price on Bazos.sk was not found.")
            return

        price_element = price_string.find_next('b')
        price = price_element.get_text().strip()
        converted_price = float(price.replace("€", "").replace(" ", "").replace(",", "."))

        exists_in_db = self.check_existing(title, converted_price)

        if not exists_in_db:
            self.store_in_db(title, converted_price)
            if self.last_price is None:
                self.send_mail("Listing Found", f"{title} \n The listing has a current price of {price}.")
            elif self.last_price < converted_price:
                self.send_mail("Price Increased", f"{title} \n The listing price increased from {self.last_price}€ to {converted_price}€.")
            elif self.last_price > converted_price:
                self.send_mail("Price Decreased", f"{title} \n The listing price decreased from {self.last_price}€ to {converted_price}€.")
            else:
                self.send_mail("Price Unchanged", f"{title} \n The listing price remains the same at {converted_price}€ as before.")
        elif self.last_price == converted_price:
            self.send_mail("Price Unchanged", f"{title} \n The listing price remains the same at {converted_price}€ as before.")
        else:
            print("The listing with a different price already exists. Not saving or sending an email.")

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
