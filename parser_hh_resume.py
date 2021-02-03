import requests
import csv
import zipfile
import pathlib
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.116 Safari/537.36',
           'Cache-Control': 'no-cache'}

base_url = 'https://hh.ru/search/resume?L_is_autosearch=false&area=1&clusters=true&exp_period=all_time&logic=normal&no_magic=false&order_by=relevance&pos=full_text&search_period=3&text=python'

# browser = webdriver.Chrome('chromedriver.exe')


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
        # browser.get(url)
        soup = bs(request.content, 'lxml')
        divs = soup.find_all('div', attrs={'class': 'resume-search-item'})
        for div in divs:
            try:
                title = div.find('a', attrs={'data-qa': 'resume-serp__resume-title'}).text
                age = div.find('span', attrs={'data-qa': 'resume-serp__resume-age'}).text
                if div.find('div', attrs={'class': 'resume-search-item__compensation'}) is None:
                    salary = ''
                else:
                    salary = div.find('div', attrs={'class': 'resume-search-item__compensation'}).text
                href = div.find('a', attrs={'data-qa': 'resume-serp__resume-title'})['href']
                if div.find('div', attrs={'data-qa': 'resume-serp__resume-excpirience-sum'}) is None:
                    excpirience_sum = ''
                else:
                    excpirience_sum = div.find('div', attrs={'data-qa': 'resume-serp__resume-excpirience-sum'}).text
                if div.find('span', attrs={'class': 'resume-search-item__company-name'}) is None:
                    company = ''
                else:
                    company = div.find('span', attrs={'class': 'resume-search-item__company-name'}).text

                if div.find('button', attrs={'class': 'bloko-link-switch'}) is None:
                    post = ''
                else:
                    post = div.find('button', attrs={'class': 'bloko-link-switch'}).text

                # browser.find_element_by_xpath(f"//button[contains(text(),'{post}')]").click()
                # time.sleep(0.5)
                # lastexp = browser.find_element_by_xpath('//div[@class="output-lastexp__text HH-ExperienceDescriptionLoader-Output"]').text
                # print(lastexp)
                # driver.find_elements_by_xpath("//*[@class='sfibbbc' or @class='jsb']")
                # driver.find_element_by_xpath('//div[@id="abc" and @class="xyz"]')

                jobs.append({
                    'title': title,
                    'age': age,
                    'salary': salary,
                    'href': 'https://hh.ru' + href,
                    'excpirience_sum': excpirience_sum,
                    'company': company,
                    # 'lastexp': lastexp,
                    'post': post
                })
                # print(title)
            except:
                pass
        print(len(jobs))
    else:
        print('Error or Done. Status code = ' + str(request.status_code))
    return jobs


# запись в csv и упаковка в zip
def csv_writer(jobs):
    # with open('parsed_jobs.csv', 'w', newline='', encoding='utf-8') as csv_file:
    with open('parsed_hh_resume.csv', 'w', newline='', encoding='cp1251', errors='replace') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(('Название вакансии', 'Возраст', 'Желаемая ЗП', 'URL', 'Опыт работы', 'Последнее место работы',
                         'Должность'))
        for job in jobs:
            writer.writerow((job['title'], job['age'], job['salary'], job['href'], job['excpirience_sum'],
                             job['company'], job['post']))
    # zip file
    my_zipfile = zipfile.ZipFile("parsed_hh_resume.zip", mode='w', compression=zipfile.ZIP_DEFLATED)
    my_zipfile.write("parsed_hh_resume.csv")
    # print(my_zipfile)
    my_zipfile.close()
    # rem file
    file_to_rem = pathlib.Path('parsed_hh_resume.csv')
    file_to_rem.unlink()


jobs = hh_parse(base_url, headers)
csv_writer(jobs)
# browser.quit()
