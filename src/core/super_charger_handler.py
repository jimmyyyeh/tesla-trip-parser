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

import pandas as pd
import requests

from app import db
from tesla_trip_common.models import SuperCharger


class SuperChargerHandler:
    @staticmethod
    def _get_old_super_chargers():
        super_chargers = SuperCharger.query.all()
        return {super_charger.name: super_charger for super_charger in super_chargers}

    @staticmethod
    def _fetch_data():
        url = 'https://teslagu.ru/supercharger/'
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43'
        }
        response = requests.get(url, headers=headers)
        table_df = pd.read_html(response.text)[0]
        table_df = table_df[['地點', '縣市', 'TPC', 'CCS2', '樓層', '營業時間', '停車收費', '充電費率', '版本']]
        table_df = table_df.fillna('…')
        table_df = table_df.replace('…', None)
        data_list = table_df.to_dict('records')
        return data_list

    @classmethod
    def _insert_data(cls, data_list):
        old_super_chargers = cls._get_old_super_chargers()
        for data in data_list:
            name = data['地點']
            if name in old_super_chargers:
                super_charger = old_super_chargers[name]
                super_charger.city = data['縣市']
                super_charger.tpc = data['TPC']
                super_charger.ccs2 = data['CCS2']
                super_charger.business_hours = data['營業時間']
                super_charger.park_fee = data['停車收費']
                super_charger.charger_fee = data['充電費率']
                super_charger.version = data['版本']
            else:
                super_charger = SuperCharger(
                    name=data['地點'],
                    city=data['縣市'],
                    tpc=data['TPC'],
                    ccs2=data['CCS2'],
                    floor=data['樓層'],
                    business_hours=data['營業時間'],
                    park_fee=data['停車收費'],
                    charger_fee=data['充電費率'],
                    version=data['版本']
                )
                db.session.add(super_charger)
        db.session.commit()

    @classmethod
    def exec(cls):
        data_list = cls._fetch_data()
        cls._insert_data(data_list=data_list)


if __name__ == '__main__':
    SuperChargerHandler.exec()
