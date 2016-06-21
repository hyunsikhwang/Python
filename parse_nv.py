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
    
    name = js['result']['areas'][0]['datas'][0]['nm']
    quote = url[-6:]
    price_t = js['result']['areas'][0]['datas'][0]['nv']
    price_y = js['result']['areas'][0]['datas'][0]['sv']
    price_ud = (price_t - price_y) / float(price_y) * 100.0
    print "%s %s %s %4.2f%%" % name, quote, price_t,  price_ud

CollectPrices(url_quote + "058470")
CollectPrices(url_quote + "042700")
CollectPrices(url_quote + "003650")
CollectPrices(url_quote + "026960")
CollectPrices(url_quote + "052330")
CollectPrices(url_quote + "036190")
CollectPrices(url_quote + "051360")
CollectPrices(url_quote + "122630")
CollectPrices(url_quote + "114800")

#processing end
end_time = time.time()

#
print end_time - start_time
