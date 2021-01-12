from urllib.parse import urljoin

import bs4
from requests import get

from Lesson03 import database


class ParserGBPost:
    def __init__(self, url, dbase):
        self.db = dbase
        self.url = url
        self.post_urls = []

    def run(self):
        # получаем список адресов блогов
        lst_url_post = self.collect_url_post()

    def _get(self, url: str) -> bs4.BeautifulSoup:
        response = get(url)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def collect_url_post(self):
        print(f'парсер и строка {self.url}')
        # определяем число страниц с блогами
        # переменной count_page_post присваиваем максимальное значение
        count_page_post = max(
            [int(i.text) for i in list(self._get(self.url).find('ul', attrs={'class': 'gb__pagination'}).children) if
             i.text.isdigit()])
        # перебираем страницы с блогами
        # в список post_urls добавляем адреса страниц блогов
        for i in range(1, count_page_post + 1):
            soup = self._get(urljoin(self.url, f'/posts?page={i}')).find('div', attrs={'class': 'post-items-wrapper'})
            for itm in soup:
                self.post_urls.append(urljoin(self.url, itm.find('a').get('href')))
        else:
            print(self.post_urls)


if __name__ == '__main__':
    db = database.Database("sqlite:///gb_blog.db")
    parser = ParserGBPost('https://geekbrains.ru/posts', db)
    parser.run()
