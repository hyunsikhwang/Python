# -*- coding: utf-8 -*-
import json
import urllib2
import time

#processing start
start_time = time.time()

url_quote = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:"  # 종목 시세 주소

def CollectPrices(url):
    f = urllib2.urlopen(url)
    page = f.read().decode('euc-kr', 'ignore')
    f.close()
    js = json.loads(page)
    return js

StockInfo = CollectPrices(url_quote+"058470")

print StockInfo['result']['areas'][0]['datas'][0]['nv']
print StockInfo['result']['areas'][0]['datas'][0]['nm']

#processing end
end_time = time.time()

#
print end_time - start_time
