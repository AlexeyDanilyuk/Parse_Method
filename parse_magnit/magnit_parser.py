import datetime
import os
import time
import requests
import bs4
from urllib.parse import urljoin
from pymongo import MongoClient
import dotenv

dotenv.load_dotenv('.env')


class StatusCodeError(Exception):
    def __init__(self, text):
        self.text = text


class MagnitParser:
    def __init__(self, url, db_client):
        self.url = url
        self.collection = db_client['gb_parse_12']['magnit']

    @staticmethod
    def _get_response(url: str, **kwargs):
        while True:
            try:
                response = requests.get(url, **kwargs)
                if response.status_code == 200:
                    return response
                raise StatusCodeError(f'{response.status_code} -> {response.text}')
            except (requests.exceptions.HTTPError,
                    requests.exceptions.ConnectTimeout,
                    StatusCodeError
                    ):
                time.sleep(0.25)

    @staticmethod
    def _get_soup(response: requests.Response) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        return soup

    def _get_product(self, soup: bs4.BeautifulSoup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        for tag_product in catalog.find_all('a', recursive=False):
            yield self._product_parse(tag_product)

    def _product_parse(self, tag_product: bs4.Tag) -> dict:
        try:
            new = list(tag_product.findNext("div", attrs={"class": "label__price label__price_new"}))
            new_price = f'{new[1].contents[0]}.{new[3].contents[0]}'
        except:
            new_price = 0.00
        try:
            old = list(tag_product.findNext("div", attrs={"class": "label__price label__price_old"}))
            old_price = f'{old[1].contents[0]}.{old[3].contents[0]}'
        except:
            old_price = 0.00

        product = {
            'url': urljoin(self.url, tag_product.get('href')),
            'promo_name': tag_product.contents[1].string,
            'product_name': list(tag_product.findNext('div', attrs={'class': 'card-sale__title'}))[0].contents[0],
            'old_price': float(old_price),
            'new_price': float(new_price),
            'image_url': urljoin(self.url, list(tag_product.find('picture'))[1].attrs['data-srcset']),
            'date_from': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_to': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        return product

    def run(self):
        page_soup = self._get_soup(self._get_response(self.url))
        for product in self._get_product(page_soup):
            self.save_rec(product)

    def save_rec(self, product: dict):
        self.collection.insert_one(product)


if __name__ == '__main__':
    db_client = MongoClient(os.getenv('MONGO_DB_URL'))
    parser = MagnitParser('https://magnit.ru/promo/?geo=moskva', db_client)
    parser.run()
