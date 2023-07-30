import requests
from bs4 import BeautifulSoup


URL = 'https://reality.bazos.sk/inzerat/153724690/2-izbovy-svetly-byt-v-tichej-lokalite-ul-karpatska-sekcov.php'

my_headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

page = requests.get(URL, headers=my_headers)

soup = BeautifulSoup(page.content, 'html.parser')

# print(soup.prettify())

title = soup.find(class_="nadpisdetail").get_text()
# price = soup.find(id="" or class_="").get_text()
# converted_price = float(price[0:5]) - not realy for me
# print(converted_price)

print(title.strip())