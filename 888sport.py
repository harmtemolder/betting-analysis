from bs4 import BeautifulSoup
import requests

url = 'https://www.888sport.com/football-betting/'
r = requests.get(url)
html = r.text
soup = BeautifulSoup(html, 'html.parser')

print('888sport: Got a soup of today\'s odds. Now what?')
