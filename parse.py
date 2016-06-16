#-*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import time
import pprint

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

def PrintStock(quote):
    print quote, MyPrettyPrinter().pformat(D[quote]), MyPrettyPrinter().pformat(E[quote]), MyPrettyPrinter().pformat(F[quote])

