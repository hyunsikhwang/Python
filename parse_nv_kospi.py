# -*- coding: utf-8 -*-
import json
import urllib2
import time

#processing start
start_time = time.time()

url_quote = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_INDEX:"  # 종목 시세 주소

def CollectPrices(url):
    f = urllib2.urlopen(url)
    page = f.read().decode('euc-kr', 'ignore')
    f.close()
    js = json.loads(page)
    
    name = js['result']['areas'][0]['datas'][0]['cd']
    quote = url[-6:]
    price_t = js['result']['areas'][0]['datas'][0]['nv']
    price_y = js['result']['areas'][0]['datas'][0]['cv']
    price_ud = price_y / float(price_y) * 100.0
    print "%s %s %.2f%% %.2f%%" % (name, quote, price_t/100.0, price_ud/100.0)

CollectPrices(url_quote + "KOSPI")
CollectPrices(url_quote + "KOSDAQ")

#processing end
end_time = time.time()

#
print end_time - start_time
