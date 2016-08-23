#-*- coding: utf-8 -*-

import urllib2
from lxml import etree
import time

#processing start
start_time = time.time()

# year 파라미터를 "오늘 기준 년도 - 1" 로 설정해야 함
url_KSP ='http://api.seibro.or.kr/openapi/service/StockSvc/getDividendRank?ServiceKey=CJL9jdtz5gsb4z4PpjFpCDjdz/UIk8cFAGgHbJvgLEJxPWLZaTx3wIcBNPkGu/KIKsI1zAy1XtfQJLG0VV0vVg==&stkTpcd=1&listTpcd=11&rankTpcd=1&year=2015'
url_KSQ ='http://api.seibro.or.kr/openapi/service/StockSvc/getDividendRank?ServiceKey=CJL9jdtz5gsb4z4PpjFpCDjdz/UIk8cFAGgHbJvgLEJxPWLZaTx3wIcBNPkGu/KIKsI1zAy1XtfQJLG0VV0vVg==&stkTpcd=1&listTpcd=12&rankTpcd=1&year=2015'

fp = urllib2.urlopen(url_KSP)
doc_KSP = etree.parse(fp)
fp = urllib2.urlopen(url_KSQ)
doc_KSQ = etree.parse(fp)
fp.close()

doc_Stock = doc_KSP.xpath('//item') + doc_KSQ.xpath('//item')

stocklist = ['058470', '026960', '042700', '003650', '052330', '036190', '114090', '051360', '034230']

for record in doc_Stock:
    stockcode = record.xpath("./shotnIsin/text()")
    stockname = record.xpath("./korSecnNm/text()")
    stockdiv = record.xpath("./divAmtPerStk/text()")
    
    for sm in stocklist:
        if stockcode[0] == sm:
            print stockcode[0], stockname[0], stockdiv[0]

#processing end
end_time = time.time()

#
print end_time - start_time
