import requests
import pandas as pd
from bs4 import BeautifulSoup

URL = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
HEADERS = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}

data_list = []

def scrape_additional_details(product_url, product_name, product_price, product_rating, num_reviews):
    response = requests.get(product_url, headers=HEADERS)
    product_soup = BeautifulSoup(response.content, 'html.parser')

    asin = product_soup.select_one('#detailBullets_feature_div li:has(span:contains("ASIN")) span.a-list-item > span:last-child')
    manufacturer = product_soup.select_one('#detailBullets_feature_div li:has(span:contains("Manufacturer")) span.a-list-item > span:last-child')
    if asin == None or manufacturer == None:
        asin = 'None'
        manufacturer = 'None'
        try:
            print(asin)
            print(manufacturer)
            table_rows = product_soup.find('table', {'id': 'productDetails_techSpec_section_1'}).find_all('tr')
            for row in table_rows:
                th = row.find('th', {'class': 'a-color-secondary a-size-base prodDetSectionEntry'})
                if th:
                    th_text = th.get_text(strip=True)
                    if th_text == 'ASIN':
                        asin_td = row.find('td', {'class': 'a-size-base prodDetAttrValue'})
                        asin = asin_td.get_text(strip=True)
                    elif th_text == 'Manufacturer':
                        manufacturer_td = row.find('td', {'class': 'a-size-base prodDetAttrValue'})
                        manufacturer = manufacturer_td.get_text(strip=True)
            print(asin)
            print(manufacturer)
        except:
            pass
    else :
        asin = asin.text
        manufacturer = manufacturer.text


    try:
        description = product_soup.find('div', {'id': 'feature-bullets'}).get_text(strip=True)
    except:
        description = 'None'
    try:
        product_description = product_soup.find('div', {'id': 'productDescription'}).get_text(strip=True)
    except:
        product_description = 'None'

    if num_reviews=='None':
        try:
            num_reviews = product_soup.select_one('#acrCustomerReviewText').get_text(strip=True).replace(',', '').split()[0]
        except:
            pass

    data_list.append({
        'Product Name': product_name,
        'Product URL': product_url,
        'Product Price': product_price,
        'Product Rating': product_rating,
        'Number of Reviews': num_reviews,
        'ASIN' : asin,
        'Manufacturer' : manufacturer,
        'Description' : description,
        'Product Description'  :product_description
    })




def scrape_detail(p):
    try:
        product_name = p.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text.strip()
    except:
        product_name = 'None'
    try:
        product_url = 'https://www.amazon.in' + p.find('a', {'class': 'a-link-normal'})['href']
    except:
        product_url = 'None'
    try:
        product_price = p.find('span', {'class': 'a-price-whole'}).text.strip().replace(',', '')
    except:
        product_price = 'None'
    try:
        product_rating = p.find('span', {'class': 'a-icon-alt'}).text.strip()
    except:
        product_rating = 'None'
    try :
        num_reviews = p.find('span', {'class': 'a-size-base s-underline-text'}).text.replace('(', '').replace(')', '').replace(',', '')
        if num_reviews=='':
            num_reviews = 'None'
    except:
        num_reviews = 'None'


    print (product_url)
    scrape_additional_details(product_url, product_name, product_price, product_rating, num_reviews)




product_count = 1

def load_page(page_no):
    global product_count, URL
    webpage = requests.get(url=URL, headers=HEADERS)

    soup = BeautifulSoup(webpage.content, 'html.parser')


    products = soup.find_all('div', {'data-component-type': 's-search-result'})
    for p in products:
        # print("------------------------------",product_count,"------------------------")
        scrape_detail(p)
        product_count+=1

    URL = 'https://www.amazon.in' + soup.find('a', {'aria-label': f'Go to page {page_no}'})['href']

page_no = 1
for i in range(15):
    page_no+=1
    try:
        load_page(page_no)
    except:
        break

df = pd.DataFrame(data_list)
df.to_csv('amazon_products.csv', index=False)