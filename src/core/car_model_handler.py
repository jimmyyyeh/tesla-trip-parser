# -*- coding: utf-8 -*
"""
      ┏┓       ┏┓
    ┏━┛┻━━━━━━━┛┻━┓
    ┃      ☃      ┃
    ┃  ┳┛     ┗┳  ┃
    ┃      ┻      ┃
    ┗━┓         ┏━┛
      ┗┳        ┗━┓
       ┃          ┣┓
       ┃          ┏┛
       ┗┓┓┏━━━━┳┓┏┛
        ┃┫┫    ┃┫┫
        ┗┻┛    ┗┻┛
    God Bless,Never Bug
"""

import re
import requests
from threading import Thread
from bs4 import BeautifulSoup

from app import db
from tesla_trip_common.models.models import CarModel


class CarModelHandler:
    _MODEL_PATTERN = re.compile(r'Model\s.+')

    @staticmethod
    def _get_old_car_models():
        car_models = CarModel.query.all()
        return {f'{car_model.model}-{car_model.spec}' for car_model in car_models}

    @classmethod
    def _fetch_detail_data(cls, url, model_dict):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'class': 'model-title'}).text
        title = cls._MODEL_PATTERN.search(title).group()
        if title not in model_dict:
            model_dict[title] = set()
        model_list = soup.find_all('div', {'class': 'model-title'})
        for model in model_list:
            model_dict[title].add(model.text)

    @classmethod
    def _fetch_data(cls, model_dict):
        url = 'https://autos.yahoo.com.tw/new-cars/make/tesla'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        year_list = soup.find_all('div', {'class', 'year'})
        thread_list = list()
        for year in year_list:
            gabtn_list = year.find_all('a', {'class': 'gabtn'}, href=True)
            for gabtn in gabtn_list:
                url = gabtn.get('href')
                thread = Thread(
                    target=cls._fetch_detail_data,
                    args=(url, model_dict,)
                )
                thread.start()
                thread_list.append(thread)
        for thread in thread_list:
            thread.join(timeout=10)

    @classmethod
    def _insert_data(cls, model_dict):
        old_car_models = cls._get_old_car_models()
        for model, spec_list in model_dict.items():
            for spec in spec_list:
                key = f'{model}-{spec}'
                if key not in old_car_models:
                    car_model = CarModel(
                        model=model,
                        spec=spec
                    )
                    db.session.add(car_model)
        db.session.commit()

    @classmethod
    def exec(cls):
        model_dict = dict()
        cls._fetch_data(model_dict=model_dict)
        cls._insert_data(model_dict=model_dict)


if __name__ == '__main__':
    CarModelHandler.exec()
