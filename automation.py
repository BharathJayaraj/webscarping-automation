import os
import re
import csv
import requests
import PyPDF2
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup
from tkinter import Tk, Label, Entry, Button

# Create a directory to store PDF files if it does not exist
if not os.path.exists('Pdf Files'):
    os.makedirs('Pdf Files')


# Define a function to remove irrelevant data from web page text
def remove_irrelevant(text):
    clean_text = re.sub(r'\n+', '\n', text)
    clean_text = re.sub(r'\t+', '', clean_text)
    clean_text = re.sub(r'\r+', '', clean_text)
    return clean_text.strip()


# Define a function to download PDF files
def download_pdf(url):
    r = requests.get(url, stream=True)
    filename = 'Pdf Files/' + urllib.parse.unquote(os.path.basename(url))
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename


# Define a function to extract tables from PDF files
def extract_tables(filename):
    tables = []
    with open(filename, 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        for i in range(reader.getNumPages()):
            page = reader.getPage(i)
            text = page.extractText()
            if 'Table' in text:
                df = pd.DataFrame([line.split('\t') for line in text.split('\n') if line])
                tables.append(df)
    return tables


# Define a function to scrape web pages and save data in CSV and Excel files
def scrape_webpages(query, num_pages):
    # Create a CSV file to store result URLs
    with open('results.csv', mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['URL'])

    # Scrape web pages and save data in Excel file
    df = pd.DataFrame(columns=['URL', 'Title', 'Text'])
    for i in range(num_pages):
        url = f'https://www.google.com/search?q={query}&start={i * 10}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for result in soup.find_all('div', class_='r'):
            link = result.find('a')['href']
            if 'pdf' in link:
                download_pdf(link)
            else:
                response = requests.get(link, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.text
                text = remove_irrelevant(soup.get_text())
                df = df.append({'URL': link, 'Title': title, 'Text': text}, ignore_index=True)
            with open('results.csv', mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([link])

    # Save data in Excel file with separate sheets for each table in PDF files
    writer = pd.ExcelWriter('output.xlsx')
    df.to_excel(writer, sheet_name='Web Pages', index=False)
    for filename in os.listdir('Pdf Files'):
        if filename.endswith('.pdf'):
            tables = extract_tables('Pdf Files/' + filename)
            for i, table in enumerate(tables):
                table.to_excel(writer, sheet_name=f'{filename[:-4]}_{i}', index=False)
