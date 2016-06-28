from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

APIKey = "CJL9jdtz5gsb4z4PpjFpCDjdz/UIk8cFAGgHbJvgLEJxPWLZaTx3wIcBNPkGu/KIKsI1zAy1XtfQJLG0VV0vVg=="

def FindCodeAPI(APIKey, stock_name):
  url = 'http://api.seibro.or.kr/openapi/service/StockSvc/getStkIsinByNm'
  queryParams = '?' + urlencode({ quote_plus('ServiceKey') : APIKey, quote_plus('secnNm') : stock_name, quote_plus('pageNo') : '2', quote_plus('numOfRows') : '2' })

  request = Request(url + queryParams)
  request.get_method = lambda: 'GET'
  response_body = urlopen(request).read()
  print response_body

FindCodeAPI(APIKey, u'삼성')
