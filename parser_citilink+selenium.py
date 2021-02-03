import requests
import csv
import zipfile
import pathlib
import time
import random
from bs4 import BeautifulSoup as bs
from selenium import webdriver

headers = {'Accept': '*/*',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.116 Safari/537.36'}

base_url = 'https://www.citilink.ru/catalog/mobile/smartfony/?available=1&space=msk_cl:&sorting=name_asc'

browser = webdriver.Chrome()

def citilink_parse(base_url, headers):
    urls = []
    products = []
    proxies = {'http': '94.141.120.28:49139'}
    # proxy = random.randint(0, len(ip_addresses) - 1)
    session = requests.Session()  # видимость того что один пользователь просмтривает много инфы
    request = session.get(base_url, headers=headers, proxies=proxies)  # эмуляция открыия страницы в браузере
    if request.status_code == 200:
        soup = bs(request.content, 'lxml')  # получаем весь контент
        try:
            pagination = soup.find_all('li', attrs={'class': 'last'})
            count = int(pagination[-1].text)
            for i in range(2):
                url = f'{base_url}&p={i + 1}'
                if url not in urls:
                    urls.append(url)
                    # print(url)
        except:
            pass
    for url in urls:
        request = session.get(url, headers=headers)
        browser.get(url)
        soup = bs(request.content, 'lxml')
        divs = soup.find_all('div', attrs={'class': 'subcategory-product-item'})
        # divs = browser.find_elements_by_xpath('//*[@class="js--subcategory-product-item subcategory-product-item product_data__gtm-js  product_data__pageevents-js ddl_product"]')
        for div in divs:
            try:
                product = div.find('a', attrs={'class': 'ddl_product_link'}).text
                href = div.find('a', attrs={'class': 'ddl_product_link'})['href']
                price = div.find('ins', attrs={'class': 'subcategory-product-item__price-num'}).text
                description = div.find('p', attrs={'class': 'short_description'}).text

                # product = div.find_element_by_xpath('//*[@class="link_gtm-js link_pageevents-js ddl_product_link"]').text
                # time.sleep(0.2)
                # print(product)

                products.append({
                    'product': product.strip(),
                    'href': href,
                    'price': price.strip(),
                    'description': description.strip().replace('\n', ''),
                    # 'url_photo': url_photo
                })
                print(product.strip())
            except:
                pass
        print(len(products))
        time.sleep(2)
    else:
        print('Error or Done. Status code = ' + str(request.status_code))
    return products


# запись в csv и упаковка в zip
def csv_writer(products):
    with open('parsed_citilink_smartfony.csv', 'w', newline='', encoding='cp1251', errors='replace') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(('Наименование товара', 'Цена', 'Ссылка на товар', 'Краткое описание'))
        for product in products:
            writer.writerow((product['product'], product['price'], product['href'], product['description']))
    # zip file
    my_zipfile = zipfile.ZipFile("parsed_citilink_smartfony.zip", mode='w', compression=zipfile.ZIP_DEFLATED)
    my_zipfile.write("parsed_citilink_smartfony.csv")
    # print(my_zipfile)
    my_zipfile.close()
    # rem file
    file_to_rem = pathlib.Path('parsed_citilink_smartfony.csv')
    file_to_rem.unlink()


products = citilink_parse(base_url, headers)
csv_writer(products)
browser.quit()
