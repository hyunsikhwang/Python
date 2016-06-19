#-*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import time
import pprint

#processing start
start_time = time.time()

url_quote = "http://finance.daum.net/item/main.daum?code=058470"  # 종목 시세 주소


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
    page = f.read().decode('utf-8', 'ignore')
    f.close()

    soup = BeautifulSoup(page, 'html.parser', from_encoding='utf-8')

    editData_table = soup.find('ul', {'class' : "list_stockrate"})
    editData_title = editData_table.findAll("li")

    i = 0
    
    for li in editData_title:
        i = i + 1
        if i <= 3:
            print li.text

    
CollectPrices(url_quote)


#processing end
end_time = time.time()

#
print end_time - start_time
