# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import time
import pprint
from xml.etree.ElementTree import parse

#processing start
start_time = time.time()

url_quote = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:"  # 종목 시세 주소


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, _object, context, maxlevels, level):
        if isinstance(_object, unicode):
            return "'%s'" % _object.encode('utf8'), True, False
        elif isinstance(_object, str):
            _object = unicode(_object,'utf8')
            return "'%s'" % _object.encode('utf8'), True, False
        return pprint.PrettyPrinter.format(self, _object, context, maxlevels, level)

def CollectPrices(url):
    f = urllib2.urlopen(url)
    page = f.read().decode('euc-kr', 'ignore')
    f.close()

    soup = BeautifulSoup(page, 'html.parser', from_encoding='euc-kr')

    editData_table = page.find('nv')
    print editData_table
    

CollectPrices(url_quote + "058470")


#processing end
end_time = time.time()

#
print end_time - start_time
