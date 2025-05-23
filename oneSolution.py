link = 'https://solve.mit.edu/solutions/8534'

from bs4 import BeautifulSoup
import requests

resp = requests.get(link)

html = resp.text

soup = BeautifulSoup(html, 'lxml')

body = soup.find('main')
body = str(body)
# print(body)

with open('8534.txt', 'w') as f:
    f.write(body)

f.close()