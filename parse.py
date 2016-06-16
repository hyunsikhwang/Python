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
global E
global F
C = {}
D = {}
E = {}
F = {}


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

    editData_table = soup.find('table', {'class' : "gTable clr"})
    editData_title = editData_table.findAll("tr")

    i = 0

    for li in editData_title:
        editData_rec = li.findAll('td')
        for li2 in editData_rec:
            soup2 = BeautifulSoup(str(li2), 'html.parser', from_encoding='utf-8')
            #print i, soup2.text

            if soup2.text <> '':
                i = i + 1
                if i % 3 == 1:
                    temp = soup2.text
                    temp2 = soup2.find('a')['href']
                    temp2 = temp2[-6:]
		    C[temp] = temp
		    D[temp] = temp2
                elif i % 3 == 2:
                    temp3 = soup2.text
		    E[temp] = temp3
                elif i % 3 == 0:
                    temp4 = soup2.text
		    F[temp] = temp4
                    #priit temp, temp2, temp3, temp4

def PrintStock(quote)
    print quote, MyPrettyPrinter().pformat(D[quote]), MyPrettyPrinter().pformat(E[quote]), MyPrettyPrinter().pformat(F[quote])

CollectPrices(url_P)
CollectPrices(url_Q)
PrintStock(u'리노공업')

#print u'리노공업', MyPrettyPrinter().pformat(D[u'리노공업']), MyPrettyPrinter().pformat(E[u'리노공업']), MyPrettyPrinter().pformat(F[u'리노공업'])
#print u'한미반도체', MyPrettyPrinter().pformat(D[u'한미반도체']), MyPrettyPrinter().pformat(E[u'한미반도체']),MyPrettyPrinter().pformat(F[u'한미반도체'])
#print u'미창석유', MyPrettyPrinter().pformat(D[u'미창석유']), MyPrettyPrinter().pformat(E[u'미창석유']), MyPrettyPrinter().pformat(F[u'미창석유'])
#print u'동서', MyPrettyPrinter().pformat(D[u'동서']), MyPrettyPrinter().pformat(E[u'동서']), MyPrettyPrinter().pformat(F[u'동서'])
#print u'코텍', MyPrettyPrinter().pformat(D[u'코텍']), MyPrettyPrinter().pformat(E[u'코텍']), MyPrettyPrinter().pformat(F[u'코텍'])
#print u'금화피에스시', MyPrettyPrinter().pformat(D[u'금화피에스시']), MyPrettyPrinter().pformat(E[u'금화피에스시']), MyPrettyPrinter().pformat(F[u'금화피에스시'])
#print u'토비스', MyPrettyPrinter().pformat(D[u'토비스']), MyPrettyPrinter().pformat(E[u'토비스']), MyPrettyPrinter().pformat(F[u'토비스'])
#print u'KODEX 레버리지', MyPrettyPrinter().pformat(D[u'KODEX 레버리지']), MyPrettyPrinter().pformat(E[u'KODEX 레버리지']), MyPrettyPrinter().pformat(F[u'KODEX 레버리지'])
#print u'KODEX 인버스', MyPrettyPrinter().pformat(D[u'KODEX 인버스']), MyPrettyPrinter().pformat(E[u'KODEX 인버스']), MyPrettyPrinter().pformat(F[u'KODEX 인버스'])
#print MyPrettyPrinter().pformat(D)
#print D
            
#processing end
end_time = time.time()

#
print end_time - start_time

