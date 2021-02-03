import requests
import csv
import zipfile
import pathlib
import time
from bs4 import BeautifulSoup as bs

base_url = 'https://www.citilink.ru/catalog/mobile/smartfony/?available=1&sorting=name_asc'

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/80.0.3987.116 Safari/537.36'
}

# pip install --user requests[socks]
proxies = {
    'http': "socks4://82.204.141.94:4145",
    'https': "socks4://82.204.141.94:4145"
}


def citilink_parse(base_url, headers):
    urls = []
    products = []

    session = requests.Session()  # видимость того что один пользователь просмтривает много инфы
    request = session.get(base_url, headers=headers, proxies=proxies)  # эмуляция открыия страницы в браузере + прокси

    if request.status_code == 200:
        soup = bs(request.content, 'lxml')  # получаем весь контент
        try:
            pagination = soup.find_all('li', attrs={'class': 'last'})
            count = int(pagination[-1].text)
            for i in range(count):
                url = f'{base_url}&p={i + 1}'
                if url not in urls:
                    urls.append(url)
                    # print(url)
        except:
            pass
    for url in urls:
        request = session.get(url, headers=headers)
        soup = bs(request.content, 'lxml')
        divs = soup.find_all('div', attrs={'class': 'subcategory-product-item'})
        for div in divs:
            try:
                product = div.find('a', attrs={'class': 'ddl_product_link'}).text
                href = div.find('a', attrs={'class': 'ddl_product_link'})['href']
                price = div.find('ins', attrs={'class': 'subcategory-product-item__price-num'}).text
                description = div.find('p', attrs={'class': 'short_description'}).text
                try:
                    url_photo = div.find('img')['src']
                except:
                    url_photo = div.find('img')['data-src']
                # [x['src'] for x in soup.findAll('img', {'class': 'sizedProdImage'})]
                products.append({
                    'product': product.strip(),
                    'href': href,
                    'price': price.strip(),
                    'description': description.strip().replace('\n                                   ', ''),
                    'url_photo': url_photo
                })
                print(product.strip(), price.strip())
            except:
                pass
        print(len(products))
        time.sleep(1)
    else:
        print('Error or Done. Status code = ' + str(request.status_code))
    return products


# запись в csv и упаковка в zip
def csv_writer(products):
    with open('parsed_citilink_smartfony.csv', 'w', newline='', encoding='cp1251', errors='replace') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(('Наименование товара', 'Цена', 'Ссылка на товар', 'Ссылка на изображение', 'Краткое описание'))
        for product in products:
            writer.writerow(
                (product['product'], product['price'], product['href'], product['url_photo'], product['description']))
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
