# -*- coding: utf-8 -*-
"""Construction_update.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zIVp6Xbt5zP6pck20iEnBLRR1mh58utx
"""

import requests
import re
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

now = datetime.datetime.now().strftime('%R')
print('Construction Update Start --',now)

print('----착공면적 업데이트----')
start = 200201 # 검색 시작 날짜

year = datetime.date.today().year
month = (datetime.date.today() + relativedelta(months = -2)).month

end = str(year) + str(month).zfill(2) # 검색 마지막 날짜

url = f'http://www.index.go.kr/strata/jsp/showStblGams3.jsp?stts_cd=122402&idx_cd=1224&freq=M&period={start}:{end}'

res = urllib.request.urlopen(url)
html = res.read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
months = soup.find_all(class_ = 'tc')

columns = []
for i in months:
    month = i.text[:4] + ' ' + i.text[4:]
    columns.append(month)

index = ['총계', '전월대비증감율', '주거용', '상업용', '농수산용', '공업용', '공공용', '교육사회용', '기타']

df_const = pd.DataFrame(index = index, columns = columns)

data_len = (int(str(end)[:4]) - int(str(start)[:4])) * 12 + int(str(end)[4:]) - int(str(start)[4:]) + 1

for i, j in enumerate(index):
    datas = soup.find_all(id = f'tr_122402_{i+1}')
    for data in datas:
        figures = re.sub(',', '', data.text).split('\n')
        df_const.loc[j] = figures[2:len(figures)-1]

df_const_sql = df_const.T.reset_index()
df_const_sql['index']
df_const_sql['연도'] = [int(year[:4]) for year in df_const_sql['index']]
df_const_sql['월'] = [int(month[4:7]) for month in df_const_sql['index']]
df_const_sql = df_const_sql[['연도', '월', '총계', '주거용', '상업용', '농수산용', '공업용', '공공용', '교육사회용', '기타']]
df_const_sql.iloc[:, 2:] = df_const_sql.iloc[:, 2:].astype('float64')

db_connection_str = 'mysql+pymysql://root:A412GBVSDsawe%$we@34.64.224.44:3306/smart_factory'
db_connection = create_engine(db_connection_str)
conn = db_connection.connect()

# df_per_sql.to_sql(name = 'building_permission',con = db_connection, index = False)
df_const_sql.to_sql(name = 'building_construction_temp',con = db_connection, index = False, if_exists = 'replace') # 테이블 삭제하고 새로 만들 때 사용
#df_per_sql.to_sql(name = 'building_construction_temp',con = db_connection, index = False, if_exists = 'append') # 데이터를 추가할 때 사용

now = datetime.datetime.now().strftime('%R')
print('Construction Update End --',now)