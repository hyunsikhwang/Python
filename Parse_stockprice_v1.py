#-*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import time
import pprint

#processing start
start_time = time.time()

url = "http://finance.daum.net/quote/all.daum?type=S&stype=Q"
f = urllib2.urlopen(url)
page = f.read().decode('utf-8', 'ignore')
f.close()

soup = BeautifulSoup(page)

editData_table = soup.find('table', {'class' : "gTable clr"})
editData_title = editData_table.findAll("tr")
#editData_title = editData_title.find_next("tr")
#editData_title = editData_title.find_next("tr")
#editData_title = editData_title.find_next("tr")
#editData_title = editData_title.find("td")
#editData_title = editData_title.find_next("td")

i = 0

D = {}

class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, _object, context, maxlevels, level):
        if isinstance(_object, unicode):
            return "'%s'" % _object.encode('utf8'), True, False
        elif isinstance(_object, str):
            _object = unicode(_object,'utf8')
            return "'%s'" % _object.encode('utf8'), True, False
        return pprint.PrettyPrinter.format(self, _object, context, maxlevels, level)

for li in editData_title:
    editData_rec = li.findAll('td')
    for li2 in editData_rec:
        soup2 = BeautifulSoup(str(li2))
        #print i, soup2
        
        if soup2.string <> None:
            i = i + 1
            if soup2.find('a') <> None:
                temp2 = soup2.find('a')['href']
                temp2 = temp2[-6:]
            if i % 3 == 1:
                temp = soup2.string
            elif i % 3 == 2:
                temp3 = soup2.string
            elif i % 3 == 0:
                temp4 = soup2.string
                D[temp] = {temp2, temp3, temp4}
                #print D

MyPrettyPrinter().pprint(D)
#print MyPrettyPrinter().pformat(D)
            
#processing end
end_time = time.time()

#print processing time
print end_time - start_time

#editDataStr = str(editData_title)

#print editDataStr

