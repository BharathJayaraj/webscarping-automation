import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.zillow.com/homes/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

for page in range(1, 21):
    res = requests.get(url, headers=headers, params={'page': page})
    soup = BeautifulSoup(res.content, 'html.parser')
    listings = soup.find_all('div', {'id':'search-page-react-content'})
    print(listings)
