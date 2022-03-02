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
from tesla_trip_common.models import AdministrativeDistrict


class AdministrativeDistrictHandler:
    @staticmethod
    def _get_old_administrative_districts():
        administrative_districts = AdministrativeDistrict.query.all()
        return {administrative_district.area for administrative_district in administrative_districts}

    @staticmethod
    def _fetch_data():
        url = 'https://zh.wikipedia.org/wiki/中華民國台灣地區鄉鎮市區列表'
        response = requests.get(url)
        table_list = pd.read_html(response.text)
        df_list = list()
        for table in table_list:
            if '轄區列表' in table.columns:
                df_list.append(table)

        df = pd.concat(df_list)
        return df

    @classmethod
    def _insert_data(cls, df):
        old_administrative_districts = cls._get_old_administrative_districts()
        for data in df.values:
            city = data[0]
            area_list = data[-1].split('、')
            for area in area_list:
                if area in old_administrative_districts:
                    continue
                administrative_district = AdministrativeDistrict(
                    city=city,
                    area=area
                )
                db.session.add(administrative_district)
        db.session.commit()

    @classmethod
    def exec(cls):
        df = cls._fetch_data()
        cls._insert_data(df=df)


if __name__ == '__main__':
    AdministrativeDistrictHandler.exec()
