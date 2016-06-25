#-*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import time
import pprint

#processing start
start_time = time.time()

url_P = "http://finance.daum.net/quote/all.daum?type=S&stype=P"  #type : U(업종순), S(가나다순)
url_Q = "http://finance.daum.net/quote/all.daum?type=S&stype=Q"  #stype : P(유가증권), Q(코스닥)

global C
global D
C = {}
D = {}


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

    soup = BeautifulSoup(page, 'lxml', from_encoding='utf-8')

    editData_table = soup.find('table', {'class' : "gTable clr"})
    editData_title = editData_table.findAll("tr")

    i = 0
    
    end_time = time.time()
    print end_time - start_time

    for li in editData_title:
        editData_rec = li.findAll('td')
        for li2 in editData_rec:
            #soup2 = BeautifulSoup(str(li2), 'lxml', from_encoding='utf-8')
            #print i, str(li2)

            if str(li2) <> '':
                i = i + 1
                if i % 3 == 1:
                    temp = str(li2)
                    temp2 = str(li2).find("a")
                    #temp2 = temp2[-6:]
	            C[temp] = temp
	            D[temp] = temp2
                    print str(li2), temp2

    end_time = time.time()
    print end_time - start_time


def PrintStock(quote):
    print quote, MyPrettyPrinter().pformat(D[quote])

CollectPrices(url_P)
CollectPrices(url_Q)
PrintStock(u'리노공업')
PrintStock(u'한미반도체')
PrintStock(u'미창석유')
PrintStock(u'동서')
PrintStock(u'코텍')
PrintStock(u'금화피에스시')
PrintStock(u'토비스')
PrintStock(u'KODEX 레버리지')
PrintStock(u'KODEX 인버스')


#processing end
end_time = time.time()
print end_time - start_time
