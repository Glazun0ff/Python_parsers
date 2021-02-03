import requests
import csv
import zipfile
import pathlib
from bs4 import BeautifulSoup as bs

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.116 Safari/537.36',
           'Cache-Control': 'no-cache'}

base_url = 'https://hh.ru/search/vacancy?area=1&search_period=3&st=searchVacancy&text=python'


def hh_parse(base_url, headers):
    jobs = []
    # urls = [base_url]
    urls = []
    session = requests.Session()  # видимость того что один пользователь просмтривает много инфы
    request = session.get(base_url, headers=headers)  # эмуляция открыия страницы в браузере
    if request.status_code == 200:
        # request = session.get(base_url, headers=headers)
        soup = bs(request.content, 'lxml')  # получаем весь контент
        try:
            pagination = soup.find_all('a', attrs={'data-qa': 'pager-page'})
            count = int(pagination[-1].text)
            for i in range(count):
                url = f'{base_url}&page={i}'
                if url not in urls:
                    urls.append(url)
        except:
            pass
        for url in urls:
            request = session.get(url, headers=headers)
            soup = bs(request.content, 'lxml')
            divs = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
            for div in divs:
                try:
                    title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
                    if div.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}) is None:
                        salary = ''
                    else:
                        salary = div.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text
                    href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
                    company = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                    text1 = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
                    text2 = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
                    content = text1 + ' ' + text2
                    jobs.append({
                        'title': title,
                        'salary': salary,
                        'href': href,
                        'company': company,
                        'content': content
                    })
                    # print(salary)
                except:
                    pass
            print(len(jobs))
    else:
        print('Error or Done. Status code = ' + str(request.status_code))
    return jobs


# запись в csv и упаковка в zip
def csv_writer(jobs):
    # with open('parsed_jobs.csv', 'w', newline='', encoding='utf-8') as csv_file:
    with open('parsed_hh_vacancy.csv', 'w', newline='', encoding='cp1251', errors='replace') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(('Название вакансии', 'Зарплата', 'URL', 'Название компании', 'Описание'))
        for job in jobs:
            writer.writerow((job['title'], job['salary'], job['href'], job['company'], job['content']))
    # zip file
    my_zipfile = zipfile.ZipFile("parsed_hh_vacancy.zip", mode='w', compression=zipfile.ZIP_DEFLATED)
    my_zipfile.write("parsed_hh_vacancy.csv")
    # print(my_zipfile)
    my_zipfile.close()
    # rem file
    file_to_rem = pathlib.Path('parsed_hh_vacancy.csv')
    file_to_rem.unlink()


jobs = hh_parse(base_url, headers)
csv_writer(jobs)
