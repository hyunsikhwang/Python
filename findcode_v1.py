# -*- coding: utf-8 -*-

from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus
from bs4 import BeautifulSoup
import pprint

APIKey = "CJL9jdtz5gsb4z4PpjFpCDjdz/UIk8cFAGgHbJvgLEJxPWLZaTx3wIcBNPkGu/KIKsI1zAy1XtfQJLG0VV0vVg=="

class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, _object, context, maxlevels, level):
        if isinstance(_object, unicode):
            return "'%s'" % _object.encode('utf8'), True, False
        elif isinstance(_object, str):
            _object = unicode(_object,'utf8')
            return "'%s'" % _object.encode('utf8'), True, False
        return pprint.PrettyPrinter.format(self, _object, context, maxlevels, level)

def FindCodeAPI(APIKey, stock_name):
  url = 'http://api.seibro.or.kr/openapi/service/StockSvc/getStkIsinByNm'
  queryParams = '?' + urlencode({ quote_plus('ServiceKey') : APIKey, quote_plus('secnNm') : stock_name, quote_plus('pageNo') : '1', quote_plus('numOfRows') : '10' })

  request = Request(url + queryParams)
  request.get_method = lambda: 'GET'
  page = urlopen(request).read()
  
  #print page

  soup = BeautifulSoup(page, 'html.parser', from_encoding='utf-8')
  
  i = 0
  retlist = []
  retlist1 = []
  retlist2 = []

  for li in soup.findAll('item'):
    i = i + 1
    #print i, li.korsecnnm.string, li.shotnisin.string
    retlist1.append(li.korsecnnm.string)
    retlist2.append(li.shotnisin.string)
    
  retlist = [retlist1, retlist2]
  return retlist

temp = FindCodeAPI(APIKey, '삼성')

for slist in temp[0]:
    MyPrettyPrinter().pprint(slist)
  
