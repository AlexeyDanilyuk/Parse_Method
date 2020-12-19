import json
import time
from pathlib import Path
import requests

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'}


class StatusCodeError(Exception):
    def __init__(self, txt):
        self.txt = txt


class ParserCategory5ka:
    def __init__(self, start_url):
        self.start_url = start_url

    def collect_categories(self):
        response = requests.get(self.start_url, headers=headers)
        return response.json()


class Parser5ka:
    def __init__(self, start_url):
        self.start_url = start_url

    def run(self, categories):
        try:
            for category in categories:
                dict_product = {
                    'name': category["parent_group_name"],
                    'code': category['parent_group_code'],
                }
                product_lst = self.parse(f'{self.start_url}?store=&records_per_page=12&page=1&categories='
                                         f'{category["parent_group_code"]}')
                if product_lst:
                    dict_product['products'] = product_lst
                    file_path = Path(__file__).parent.joinpath('products', f'{category["parent_group_name"]}.json')
                    self.save(dict_product, file_path)
        except requests.exceptions.MissingSchema:
            exit()

    def get_response(self, url, **kwargs):
        while True:
            try:
                response = requests.get(url, **kwargs)
                if response.status_code != 200:
                    raise StatusCodeError(response.status_code)
                time.sleep(0.05)
                return response
            except (requests.exceptions.HTTPError,
                    StatusCodeError,
                    requests.exceptions.BaseHTTPError,
                    requests.exceptions.ConnectTimeout):
                time.sleep(0.25)

    def parse(self, url):
        product = []
        while url:
            response = self.get_response(url, headers=headers)
            data = response.json()
            print(data['results'])
            if data['results']:
                for d in data['results']:
                    product.append(d)
            url = data['next']
        return product

    def save(self, data: dict, file_path):
        with open(file_path, 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parser5ka('https://5ka.ru/api/v2/special_offers/')
    categories = ParserCategory5ka('https://5ka.ru/api/v2/categories/')
    parser.run(categories.collect_categories())
