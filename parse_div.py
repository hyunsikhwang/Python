import lxml.etree
from urllib2 import Request, urlopen

url_KSP ='http://api.seibro.or.kr/openapi/service/StockSvc/getDividendRank?ServiceKey=CJL9jdtz5gsb4z4PpjFpCDjdz/UIk8cFAGgHbJvgLEJxPWLZaTx3wIcBNPkGu/KIKsI1zAy1XtfQJLG0VV0vVg==&stkTpcd=1&listTpcd=11&rankTpcd=1&year=2015'
url_KSQ ='http://api.seibro.or.kr/openapi/service/StockSvc/getDividendRank?ServiceKey=CJL9jdtz5gsb4z4PpjFpCDjdz/UIk8cFAGgHbJvgLEJxPWLZaTx3wIcBNPkGu/KIKsI1zAy1XtfQJLG0VV0vVg==&stkTpcd=1&listTpcd=12&rankTpcd=1&year=2015'

response = Request.get(url)

# Use `lxml.etree` rathern than `lxml.html`, 
# and unicode `response.text` instead of `response.content`
doc = lxml.etree.fromstring(response.text)

for path in doc.xpath('//shotnIsin[@name="026960"]/@value'):
     print path
