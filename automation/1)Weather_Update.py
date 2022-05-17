# -*- coding: utf-8 -*-
"""weather_db.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16w-0s0QUcxRIQ8yZTAalBfT32ckPGEHa
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import re
import math
import datetime
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, Normalizer
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sqlalchemy import create_engine
from dateutil.relativedelta import relativedelta

now = datetime.datetime.now().strftime('%R')
print('Weather Update Start --',now)

conn = pymysql.connect(host='34.64.224.44', user='root', password='A412GBVSDsawe%$we', db='smart_factory')
sql_state='SELECT * FROM `weather_day`'
weather_day=pd.read_sql_query(sql_state, conn)

start_date_=weather_day['SOLDDATE'][len(weather_day)-1].strftime('%Y-%m-%d')

now = datetime.datetime.now()

end_date_ = now - relativedelta(days=1)
end_date_ = end_date_.strftime('%Y-%m-%d')

def cat_location(x):
        if x == '서울': return 108
        elif x == '경기도북부': return 98
        elif x == '경기도남부': return 119
        elif x == '인천': return 112
        elif x == '부산광역시': return 159
        elif x == '대구광역시': return 143
        elif x == '울산광역시': return 152
        elif x == '경상북도': return 278
        elif x == '경상남도': return 263
        elif x == '전라북도': return 146
        elif x == '전라남도': return 156
        elif x == '대전광역시': return 133
        elif x == '세종시': return 133
        elif x == '충청북도': return 131
        elif x == '충청남도': return 129
        elif x == '강원도': return 114
        else: return 119 ## 해당 안될시 생판지역인 평택 기준 날씨로 변환

def loc_weather(start_date, end_date, location):
    import pandas as pd
    import requests
    import numpy as np

    start_date = start_date.replace('-','')
    end_date = end_date.replace('-','')

    location_code = cat_location(location)

    url = 'http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList'

    #servicekey = ZKOx0KH7l+PcSZZNRvuI54pjFf5gbYeIa1ccvoUcbzlwPA7ZRd9AqYB+V6++N/urN+9OncLmDH9MvqvMu5SKbg==
    #servicekey2 = p6rQtYpFx5ZivDokXiWeZEPT1qg7CGrnWM9XP9rPcOy45BUhyI3RM9OoXCo3CWSAH31Va67TZGHaOOFWN/I7Cg==

    params ={'serviceKey' : 'dDUc9SVR/pZIxs5qbu7ABEG4/S5t0ZJBTLZdlveVsR4Hyc2ynwn17cF68xglOrHN/mNu/W4JmkPP3N/M8HF12g==', 
            'pageNo' : '1', 
            'numOfRows' : '999', 
            'dataType' : 'JSON', 
            'dataCd' : 'ASOS', 
            'dateCd' : 'DAY', 
            'startDt' : start_date,
            'endDt' : end_date, 
            'stnIds' : str(location_code) }


    response = requests.get(url, params=params).json()
    r_response = response.get("response")
    r_body = r_response.get("body")
    r_items = r_body.get("items")
    r_item = r_items.get("item")

    time = [] #일자
    tem = [] #온도
    hum = [] #습도
    rain = [] #강수량
    snow = [] #적설량

    for i in range(len(r_item)):
        time.append(r_item[i]['tm'])
        tem.append(r_item[i]['avgTa'])
        hum.append(r_item[i]['avgRhm'])
        rain.append(r_item[i]['sumRn'])
        snow.append(r_item[i]['sumDpthFhsc'])

    time = pd.Series(time)
    tem = pd.Series(tem)
    hum = pd.Series(hum)
    rain = pd.Series(rain)
    snow = pd.Series(snow)

    data = [ time, tem, hum, rain, snow ]

    df = pd.concat(data, axis=1)

    df.columns = ['SOLDDATE','TEMP','HUM','RAIN','SNOW']
    df.replace('', 0,inplace=True)

    df['REGION_U'] = location
    df['SOLDDATE'] = pd.to_datetime(df['SOLDDATE'])
    df['TEMP'] = round(df['TEMP'].astype('float32'),1)
    df['HUM'] = round(df['HUM'].astype('float32'),1)
    df['RAIN'] = round(df['RAIN'].astype('float32'),1)
    df['SNOW'] = round(df['SNOW'].astype('float32'),1)

    return df

def make_weather_data():
    start_date = start_date_
    end_date = end_date_
    loc_li = ['서울','경기도북부','경기도남부','인천','부산광역시','대구광역시','울산광역시','경상북도','경상남도','전라북도','전라남도','대전광역시','세종시','충청북도','충청남도','강원도']
    
    weather_df_all = pd.DataFrame()
    for i in loc_li:
        weather_df = loc_weather(start_date,end_date,i)
        weather_df_all = pd.concat((weather_df_all, weather_df), axis = 0)
    return weather_df_all
        
df = make_weather_data()

db_connection_str = 'mysql+pymysql://root:A412GBVSDsawe%$we@34.64.224.44:3306/smart_factory'
db_connection = create_engine(db_connection_str)
conn = db_connection.connect()

# df.to_sql(name = 'building_permission',con = db_connection, index = False)
#df.to_sql(name = 'weather_day',con = db_connection, index = False, if_exists = 'replace') # 테이블 삭제하고 새로 만들 때 사용
df.to_sql(name = 'weather_day',con = db_connection, index = False, if_exists = 'append') # 데이터를 추가할 때 사용

sql_state='SELECT * FROM `weather_day`'
weather_day=pd.read_sql_query(sql_state, conn)

weather_day['Year']=weather_day['SOLDDATE'].dt.year
weather_day['Month']=weather_day['SOLDDATE'].dt.month

weather_Month=weather_day.groupby(['Year','Month','REGION_U']).mean().reset_index()

db_connection_str = 'mysql+pymysql://root:A412GBVSDsawe%$we@34.64.224.44:3306/smart_factory'
db_connection = create_engine(db_connection_str)
conn = db_connection.connect()

# df.to_sql(name = 'building_permission',con = db_connection, index = False)
#df.to_sql(name = 'weather_day',con = db_connection, index = False, if_exists = 'replace') # 테이블 삭제하고 새로 만들 때 사용
weather_Month.to_sql(name = 'weather_month',con = db_connection, index = False, if_exists = 'replace') # 데이터를 추가할 때 사용

now = datetime.datetime.now().strftime('%R')
print('Weather Update End --',now)