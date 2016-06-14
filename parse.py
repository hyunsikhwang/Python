#-*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import time
import pprint

#processing start
start_time = time.time()

url_P = "http://finance.daum.net/quote/all.daum?type=S&stype=P"  #type : U(업종순), S(가나다순)
url_Q = "http://finance.daum.net/quote/all.daum?type=S&stype=Q"  #stype : P(유가증권), Q(코스닥)

global D
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

    soup = BeautifulSoup(page)

    editData_table = soup.find('table', {'class' : "gTable clr"})
    editData_title = editData_table.findAll("tr")

    i = 0

    for li in editData_title:
        editData_rec = li.findAll('td')
        for li2 in editData_rec:
            soup2 = BeautifulSoup(str(li2))
            #print i, soup2.text

            if soup2.text <> '':
                i = i + 1
                if soup2.find('a') <> None:
                    temp2 = soup2.find('a')['href']
                    temp2 = temp2[-6:]
                if i % 3 == 1:
                    temp = soup2.text
                elif i % 3 == 2:
                    temp3 = soup2.text
                elif i % 3 == 0:
                    temp4 = soup2.text
                    D[temp] = {temp2, temp3, temp4}
                    #print D

CollectPrices(url_P)
CollectPrices(url_Q)

MyPrettyPrinter().pprint(D[u'리노공업'])
#MyPrettyPrinter().pprint(D[u'한미반도체'])
#MyPrettyPrinter().pprint(D[u'미창석유'])
#MyPrettyPrinter().pprint(D[u'동서'])
#MyPrettyPrinter().pprint(D[u'코텍'])
#MyPrettyPrinter().pprint(D[u'금화피에스시'])
#MyPrettyPrinter().pprint(D[u'토비스'])
#MyPrettyPrinter().pprint(D[u'KODEX 레버리지'])
#MyPrettyPrinter().pprint(D[u'KODEX 인버스'])
#print MyPrettyPrinter().pformat(D)
#print D
            
#processing end
end_time = time.time()

#print processing time
print end_time - start_time

