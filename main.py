#-*- coding: utf-8 -*-
#
# original:    https://github.com/yukuku/telebotuseri
# modified by: Bak Yeon O @ http://bakyeono.net
# description: http://bakyeono.net/post/2015-08-24-using-telegram-bot-api.html
# github:      https://github.com/bakyeono/using-telegram-bot-api
#

# 구글 앱 엔진 라이브러리 로드
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

# URL, JSON, 로그, 정규표현식 관련 라이브러리 로드
import urllib
import urllib2
import json
import logging
import re
import time

# 종목명 찾기 API 관련 라이브러리 로드
from urllib import urlencode, quote_plus
from urllib2 import Request, urlopen

# 파싱 관련 라이브러리 로드
import urllib2
from bs4 import BeautifulSoup
import time
import pprint

import unicodedata
import copy

# 파싱 주소
url_quote = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:"  # 종목 시세 주소
url_index = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_INDEX:" # 인덱스 조회 주소
url_quotelist_KSP = "http://finance.daum.net/quote/all.daum?type=S&stype=P"  #type : U(업종순), S(가나다순)
url_quotelist_KSD = "http://finance.daum.net/quote/all.daum?type=S&stype=Q"  #stype : P(유가증권), Q(코스닥)

APIKey = "CJL9jdtz5gsb4z4PpjFpCDjdz/UIk8cFAGgHbJvgLEJxPWLZaTx3wIcBNPkGu/KIKsI1zAy1XtfQJLG0VV0vVg=="

def preformat_cjk (string, width, align='<', fill=' '):
    count = (width - sum(1 + (unicodedata.east_asian_width(c) in "WF")
                         for c in string))
    return {
        '>': lambda s: fill * count + s,
        '<': lambda s: s + fill * count,
        '^': lambda s: fill * (count / 2)
                       + s
                       + fill * (count / 2 + count % 2)
}[align](string)


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
    queryParams = '?' + urlencode({ quote_plus('ServiceKey') : APIKey, quote_plus('secnNm') : stock_name.encode('utf-8'), quote_plus('pageNo') : '1', quote_plus(u'numOfRows') : '50' })
    
    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    page = urlopen(request).read()
    
    soup = BeautifulSoup(page, 'html.parser', from_encoding='utf-8')
    
    i = 0
    retlist = []
    retlist1 = []
    retlist2 = []
    
    for li in soup.findAll('item'):
        i = i + 1
        retlist1.append([li.korsecnnm.string])
        retlist2.append([li.shotnisin.string])
    
    retlist = [retlist1, retlist2]
    return retlist


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, _object, context, maxlevels, level):
        if isinstance(_object, unicode):
            return "'%s'" % _object.encode('utf8'), True, False
        elif isinstance(_object, str):
            _object = unicode(_object,'utf8')
            return "'%s'" % _object.encode('utf8'), True, False
        return pprint.PrettyPrinter.format(self, _object, context, maxlevels, level)


def CollectQuote(url):
    f = urllib2.urlopen(url)
    page = f.read().decode('utf-8', 'ignore')
    f.close()

    soup = BeautifulSoup(page, 'html.parser', from_encoding='utf-8')
    editData_table = soup.find('table', {'class' : "gTable clr"})
    editData_title = editData_table.findAll("tr")

    i = 0
    j = 0
    t_list = list()
    t_class = QuoteList()

    for li in editData_title:
        editData_rec = li.findAll('td')
        for li2 in editData_rec:
            if li2.text <> '':
                i = i + 1
                if i % 3 == 1:
                    stock_name = li2.text
                    pos = str(li2).find("code=") + 5
                    stock_code = str(li2)[pos:(pos+6)]
                    t_class.quote_name = stock_name
                    t_class.quote_code = stock_code
                    t_list.append(t_class)
    return t_list


def CollectIndex(url):
    f = urllib2.urlopen(url)
    page = f.read().decode('euc-kr', 'ignore')
    f.close()
    js = json.loads(page)
    
    name = js['result']['areas'][0]['datas'][0]['cd']
    price_t = js['result']['areas'][0]['datas'][0]['nv']
    price_diff = js['result']['areas'][0]['datas'][0]['cv']
    price_ud = price_diff / float(price_t + price_diff) * 100.0
    return u"<code>{0:8} {1:7.2f} {2:6.2f}%</code>\n".format(name, price_t/100.0, price_ud)

    
def CollectPrices(url):
    f = urllib2.urlopen(url)
    page = f.read().decode('euc-kr', 'ignore')
    f.close()
    js = json.loads(page)
    
    name = js['result']['areas'][0]['datas'][0]['nm']
    quote = url[-6:]
    price_t = js['result']['areas'][0]['datas'][0]['nv']
    price_y = js['result']['areas'][0]['datas'][0]['sv']
    eps = js['result']['areas'][0]['datas'][0]['eps']
    bps = js['result']['areas'][0]['datas'][0]['bps']
    price_ud = price_t - price_y
    price_udrate = price_ud / float(price_y) * 100.0
    price_tc = format(price_t, ",")
    return [u"{0} {1:8} {2:8} {3:.2f}%".format(preformat_cjk(name, 14, "<", "_"), quote, price_tc, price_udrate), price_ud, price_t, price_y, eps, bps]


def MergeList(reflist):
    ml = ""
    for il in reflist:
        ml += il[0] + "\n"
    
    return ml


# 봇 토큰, 봇 API 주소
TOKEN = '234646277:AAEl5x5nIIgu36YtQWGqJR6pLdB_0bGNUvM'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

# 봇이 응답할 명령어
CMD_START     = '/start'
CMD_STOP      = '/stop'
CMD_ADD       = '/add'
CMD_DEL       = '/del'
CMD_EDITP     = '/ep'
CMD_EDITQ     = '/eq'
CMD_LIST      = '/list'
CMD_NONE      = '/none'
CMD_HELP      = '/help'
CMD_VIEW      = '/view'
CMD_REORD     = '/reord'
CMD_BROADCAST = '/broadcast'

# 봇 사용법 & 메시지
USAGE = u"""[사용법] 아래 명령어를 메시지로 보내거나 버튼을 누르시면 됩니다.
/start - (로봇 활성화)
/stop  - (로봇 비활성화)
/add   - (종목 추가)
/del   - (종목 삭제)
/ep    - (종목 가격 수정)
/eq    - (종목 수량 수정)
/list  - (종목 열람)
/none  - (종목 추가/삭제 종료)
/view  - (수동 실행)
/reord - (종목 순서 재배치)
/help  - (이 도움말 보여주기)
"""
MSG_START = u'봇을 시작합니다.'
MSG_STOP  = u'봇을 정지합니다.'

# 커스텀 키보드
CUSTOM_KEYBOARD = [
        [CMD_START, CMD_STOP, CMD_HELP],
        [CMD_ADD, CMD_DEL, CMD_LIST, CMD_NONE],
        [CMD_EDITP, CMD_EDITQ, CMD_VIEW, CMD_REORD],
        ]

USER_KEYBOARD = []

ST_ECHO, ST_ADD, ST_DEL, ST_EDITP, ST_EDITQ, ST_EDITP_VAL, ST_EDITQ_VAL, ST_REORD, ST_REORD_RANK = range(9)

# 채팅별 로봇 활성화 상태
# 구글 앱 엔진의 Datastore(NDB)에 상태를 저장하고 읽음
# 사용자가 /start 누르면 활성화
# 사용자가 /stop  누르면 비활성화
# 사용자가 /add   누르면 종목 추가 모드 진입
# 사용자가 /del   누르면 종목 삭제 모드 진입
# 사용자가 /ep    누르면 종목 가격수정 모드 진입
# 사용자가 /eq    누르면 종목 수량수정 모드 진입
# 사용자가 /list  누르면 종목 열람 
# 사용자가 /reord 누르면 종목 순서 재배치 모드 진입
# 사용자가 /none  누르면 종목 추가/삭제/수정 모드 종료

class EnableStatus(ndb.Model):
    enabled = ndb.BooleanProperty(required=True, indexed=True, default=False,)

class CommandStatus(ndb.Model):
    command_status = ndb.IntegerProperty(required=True, indexed=True, default=False,)

class QuoteList(ndb.Model):
    quote_code = ndb.StringProperty(required=True, indexed=True, default=False,)
    quote_name = ndb.StringProperty(required=True, indexed=True, default=False,)

# ShareInfo 보유주식 정보 에 대한 NDB structured property
# stockname 주식명
# stockcode 종목코드
# noofshare 보유주식수
# avgprice 매수평단가
class ShareInfo(ndb.Model):
    stockname = ndb.StringProperty()
    stockcode = ndb.StringProperty()
    noofshare = ndb.IntegerProperty()
    avgprice = ndb.IntegerProperty()

class ChatId(ndb.Model):
    name = ndb.StringProperty()

class StockList(ndb.Model):
    userid = ndb.KeyProperty(kind=ChatId)
    info = ndb.StructuredProperty(ShareInfo, repeated=True)

class EditStock(ndb.Model):
    name = ndb.StringProperty()

class OrderNumber(ndb.Model):
    ordnum = ndb.IntegerProperty()

def set_enabled(chat_id, enabled):
    u"""set_enabled: 봇 활성화/비활성화 상태 변경
    chat_id:    (integer) 봇을 활성화/비활성화할 채팅 ID
    enabled:    (boolean) 지정할 활성화/비활성화 상태
    """
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = enabled
    es.put()


def set_status(chat_id, cmd_status):
    u"""set_status: 명령어 상태
    chat_id:    (integer) 채팅 ID
    cmd_status: (integer) 명령어 상태(add/del)
    """
    cs = CommandStatus.get_or_insert(str(chat_id))
    cs.command_status = cmd_status
    cs.put()


def set_editstock(chat_id, text):
    u"""set_editstock: 가격/수량 수정
    chat_id: (integer) 채팅 ID
    text:    (char) 종목명
    """
    se = EditStock.get_or_insert(str(chat_id))
    se.name = text
    se.put()
    

def view_list(chat_id):
    u"""view_list: 등록된 종목 리스트 출력
    chat_id:    (integer) 채팅 ID
    """
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info
    entireList = ""

    for aaa in sltemp:
        entireList += aaa.stockname + "\t" + aaa.stockcode + "\t" + format(aaa.avgprice, ",") + "\t" + format(aaa.noofshare, ",") +"\n"

    send_msg(chat_id, entireList)


def extract_list(chat_id):
    u"""extract_list: 종목 리스트 출력 (삭제 목적)
    chat_id:          (integer) 채팅 ID
    """
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info
    entireList = []
    for aaa in sltemp:
        entireList.append([aaa.stockname])
    return entireList


def extract_quote(chat_id):
    u"""extract_quote: 종목 리스트 출력 (삭제 목적)
    chat_id:          (integer) 채팅 ID
    """
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info
    entireList = []
    for aaa in sltemp:
        entireList.append([str(aaa.stockcode), aaa.noofshare])
    return entireList

def extract_quantuty(chat_id):
    u"""extract_quantity: 종목 수량 추출
    chat_id:    (integer) 채팅 ID
    """
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info
    entireList = []
    for aaa in sltemp:
        entireList.append([aaa.noofshare])
    return entireList

def set_stocklist(chat_id, sname, scode):
    u"""set_stocklist: 사용자별 종목 등록
    chat_id:    (integer) 채팅 ID
    sname:      (string)  종목명(보유주식수, 평균매수단가는 향후 추가)
    scode:      (string)  종목코드
    """
    sl = StockList.get_or_insert(str(chat_id))
    sltemp = sl.info
    # 기존에 없던 종목명일때에만 추가하는 조건문
    # sl : StockList 클래스
    # sltemp : StockList.info (NDB Structured Property, 즉 리스트) 그러면 sltemp[0], [1] 이런게 되나?
    for aaa in sltemp:
        if aaa.stockname == sname:
            send_msg(chat_id, u'이미 등록되어있는 종목입니다.')
            return
    # 새로운 레코드 추가함 / 보유주식수와 가격은 0 으로 default 처리
    sltemp.append(ShareInfo(stockname = sname, stockcode = scode, noofshare = 0, avgprice = 0))
    sl.info = sltemp
    #sl.info = [ShareInfo(stockname = stockinfo)]
    sl.put()

def get_enabled(chat_id):
    u"""get_enabled: 봇 활성화/비활성화 상태 반환
    return: (boolean)
    """
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

def get_status(chat_id):
    u"""get_status: 종목 추가/삭제 상태 반환
    return: (boolean)
    """
    cs = CommandStatus.get_by_id(str(chat_id))
    if cs:
        return cs.command_status
    return False

def get_enabled_chats():
    u"""get_enabled: 봇이 활성화된 채팅 리스트 반환
    return: (list of EnableStatus)
    """
    query = EnableStatus.query(EnableStatus.enabled == True)
    return query.fetch()

# 메시지 발송 관련 함수들
def send_msg(chat_id, text, reply_to=None, no_preview=True, keyboard=None, one_time_keyboard=False):
    u"""send_msg: 메시지 발송
    chat_id:    (integer) 메시지를 보낼 채팅 ID
    text:       (string)  메시지 내용
    reply_to:   (integer) ~메시지에 대한 답장
    no_preview: (boolean) URL 자동 링크(미리보기) 끄기
    keyboard:   (list)    커스텀 키보드 지정
    """
    params = {
        'chat_id': str(chat_id),
        'text': text.encode('utf-8'),
        }
    if reply_to:
        params['reply_to_message_id'] = reply_to
    if no_preview:
        params['disable_web_page_preview'] = no_preview
    if keyboard:
        reply_markup = json.dumps({
            'keyboard': keyboard,
            'resize_keyboard': True,
            'one_time_keyboard': one_time_keyboard,
            'selective': (reply_to == True),
            })
        params['reply_markup'] = reply_markup
    try:
        urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params) + '&parse_mode=HTML').read()
    except Exception as e:
        logging.exception(e)

def broadcast(text):
    u"""broadcast: 봇이 켜져 있는 모든 채팅에 메시지 발송
    text:       (string)  메시지 내용
    """
    for chat in get_enabled_chats():
        send_msg(chat.key.string_id(), text)

# 봇 명령 처리 함수들
def cmd_start(chat_id):
    u"""cmd_start: 봇을 활성화하고, 활성화 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    set_enabled(chat_id, True)
    send_msg(chat_id, MSG_START, keyboard=CUSTOM_KEYBOARD)

def cmd_stop(chat_id):
    u"""cmd_stop: 봇을 비활성화하고, 비활성화 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    set_enabled(chat_id, False)
    send_msg(chat_id, MSG_STOP)

def cmd_add(chat_id):
    u"""cmd_add: 종목 추가 모드
    chat_id: (integer) 채팅 ID
    """
    set_status(chat_id, ST_ADD)
    send_msg(chat_id, u'추가할 종목 이름을 입력하세요.')
    
def cmd_del(chat_id):
    u"""cmd_del: 종목 삭제 모드
    chat_id: (integer) 채팅 ID
    """
    set_status(chat_id, ST_DEL)
    DelKBD = extract_list(chat_id)
    DelKBD.append([CMD_NONE])
    USER_KEYBOARD = DelKBD
    send_msg(chat_id, u'삭제할 종목 이름을 입력(선택)하세요.', keyboard=USER_KEYBOARD)

def cmd_editp(chat_id):
    u"""cmd_editp: 종목 가격 수정 모드
    chat_id: (integer) 채팅 ID
    """
    set_status(chat_id, ST_EDITP)
    EditKBD = extract_list(chat_id)
    EditKBD.append([CMD_NONE])
    USER_KEYBOARD = EditKBD
    send_msg(chat_id, u'가격을 수정할 종목 이름을 입력(선택)하세요.', keyboard=USER_KEYBOARD)

def cmd_editq(chat_id):
    u"""cmd_editq: 종목 수량 수정 모드
    chat_id: (integer) 채팅 ID
    """
    set_status(chat_id, ST_EDITQ)
    EditKBD = extract_list(chat_id)
    EditKBD.append([CMD_NONE])
    USER_KEYBOARD = EditKBD
    send_msg(chat_id, u'수량을 수정할 종목 이름을 입력(선택)하세요.', keyboard=USER_KEYBOARD)

def cmd_list(chat_id):
    u"""cmd_list: 등록된 종목 열람
    chat_id: (integer) 채팅 ID
    """
    view_list(chat_id)

def cmd_none(chat_id):
    u"""cmd_none: 종목 추가/삭제 모드 종료
    chat_id: (integer) 채팅 ID
    """
    set_status(chat_id, ST_ECHO)
    send_msg(chat_id, u'종목 추가/삭제가 종료되었습니다.', keyboard=CUSTOM_KEYBOARD)

def cmd_addquote(chat_id, text, result_list):
    u"""cmd_addquote: 종목 추가
    chat_id: (integer) 채팅 ID
    """
    USER_KEYBOARD = result_list
    send_msg(chat_id, u'종목을 선택해주십시오.\n선택 작업 종료는 /none 을 선택해주세요.', keyboard=USER_KEYBOARD)

def cmd_delquote(chat_id, text):
    u"""cmd_delquote: 종목 삭제
    chat_id: (integer) 채팅 ID
    """
    
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info
    sindex = 0
    for aaa in sltemp:
        if aaa.stockname == text:
            sltemp.pop(sindex)
            sl.info = sltemp
            sl.put()
            #사용자정의키보드(종목리스트) refresh
            DelKBD = extract_list(chat_id)
            DelKBD.append([CMD_NONE])
            USER_KEYBOARD = DelKBD
            send_msg(chat_id, text + u' 종목이 삭제되었습니다.', keyboard=USER_KEYBOARD)
            return
        sindex = sindex + 1

def cmd_editprice(chat_id, text):
    u"""cmd_editprice: 가격 수정할 종목명 입력
    chat_id: (integer) 채팅 ID
    text   : (char)    종목명
    """
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info
    #sindex = 0
    for aaa in sltemp:
        if aaa.stockname == text:
            #sltemp[sindex].avgprice = text
            #sl.info = sltemp
            #sl.put()
            set_editstock(chat_id, text)
            send_msg(chat_id, text + u'의 평균매수단가를 입력해주세요.')
            set_status(chat_id, ST_EDITP_VAL)
            return
        #sindex = sindex + 1
    send_msg(chat_id, u'종목명을 다시 확인해주세요.')
    return

def cmd_editprice_val(chat_id, text):
    u"""cmd_editprice_val: 종목별 평균매수단가 입력
    chat_id: (integer) 채팅 ID
    text   : (char)    매수단가
    """
    sl = StockList.get_by_id(str(chat_id))
    esname = EditStock.get_by_id(str(chat_id))
    sltemp = sl.info
    sindex = 0
    for aaa in sltemp:
        if aaa.stockname == esname.name:
            sltemp[sindex].avgprice = int(text)
            sl.info = sltemp
            sl.put()
            send_msg(chat_id, esname.name + u'의 매수 단가가 ' + text + u'원으로 수정되었습니다.')
            set_status(chat_id, ST_EDITP)
            cmd_editp(chat_id)
            return
        sindex = sindex + 1
    cmd_editp(chat_id)
    return

def cmd_editquantity(chat_id, text):
    u"""cmd_editquantity: 종목 수량 수정
    chat_id: (integer) 채팅 ID
    text:    (chat)    종목명
    """
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info
    #sindex = 0
    for aaa in sltemp:
        if aaa.stockname == text:
            set_editstock(chat_id, text)
            send_msg(chat_id, text + u'의 보유수량을 입력해주세요.')
            set_status(chat_id, ST_EDITQ_VAL)
            return
        #sindex = sindex + 1
    send_msg(chat_id, u'종목명을 다시 확인해주세요.')
    return

def cmd_editquantity_val(chat_id, text):
    u"""cmd_editprice_val: 종목별 평균매수단가 입력
    chat_id: (integer) 채팅 ID
    text   : (char)    보유 주식수
    """
    sl = StockList.get_by_id(str(chat_id))
    esname = EditStock.get_by_id(str(chat_id))
    sltemp = sl.info
    sindex = 0
    for aaa in sltemp:
        if aaa.stockname == esname.name:
            sltemp[sindex].noofshare = int(text)
            sl.info = sltemp
            sl.put()
            send_msg(chat_id, esname.name + u'의 보유 주식수가 ' + text + u' 으로 수정되었습니다.')
            set_status(chat_id, ST_EDITQ)
            cmd_editq(chat_id)
            return
        sindex = sindex + 1
    cmd_editq(chat_id)
    return

def cmd_reord_rank(chat_id, text):
    u"""cmd_reord_rank: 등록된 종목의 순서 변경
    chat_id: (integer) 채팅 ID
    text   : (char)    종목 이름
    """
    set_status(chat_id, ST_REORD_RANK)
    stockall = ''
    stocknumber = 0

    #ReOrdKBD = extract_list(chat_id)
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info

    for aaa in sltemp:
        stocknumber += 1
        stockall = stockall + '[' + str(stocknumber) + '] ' + aaa.stockname + '\n'
        if aaa.stockname == text:
            on = OrderNumber.get_or_insert(str(chat_id))
            on.ordnum = stocknumber
            on.put()
    send_msg(chat_id, stockall)
    send_msg(chat_id, u'바꿀 위치에 해당하는 숫자를 입력해주세요.')
    return

def cmd_reord_execute(chat_id, text):
    u"""cmd_reord_execute: 등록된 종목의 순서 변경
    chat_id: (integer) 채팅 ID
    text   : (char)    바꾸려고 하는 위치(숫자)
    """
    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info

    on = OrderNumber.get_by_id(str(chat_id))
    oldrank = on.ordnum
    newrank = int(text)

    sindex = 1

    #ReOrdKBD = extract_list(chat_id)
    #NewStockList = ReOrdKBD[:]
    NewStockList = copy.deepcopy(sltemp)

    if oldrank < newrank:
        for idx in range(oldrank, newrank):
            #NewStockList[idx-1] = ReOrdKBD[idx]
            NewStockList[idx-1].stockname = sltemp[idx].stockname
            NewStockList[idx-1].stockcode = sltemp[idx].stockcode
            NewStockList[idx-1].noofshare = sltemp[idx].noofshare
            NewStockList[idx-1].avgprice = sltemp[idx].avgprice
    else:
        for idx in range(newrank+1, oldrank+1):
            #NewStockList[idx-1] = ReOrdKBD[idx-2]
            NewStockList[idx-1].stockname = sltemp[idx-2].stockname
            NewStockList[idx-1].stockcode = sltemp[idx-2].stockcode
            NewStockList[idx-1].noofshare = sltemp[idx-2].noofshare
            NewStockList[idx-1].avgprice = sltemp[idx-2].avgprice

    #NewStockList[newrank-1] = ReOrdKBD[oldrank-1]
    NewStockList[newrank-1].stockname = sltemp[oldrank-1].stockname
    NewStockList[newrank-1].stockcode = sltemp[oldrank-1].stockcode
    NewStockList[newrank-1].noofshare = sltemp[oldrank-1].noofshare
    NewStockList[newrank-1].avgprice = sltemp[oldrank-1].avgprice

    sl.info = NewStockList
    sl.put()

#    for aaa in NewStockList:
#        send_msg(chat_id, aaa.stockname)
#    send_msg(chat_id, u'순서를 잘못 입력하셨습니다. 다시 확인해주세요.')    
    cmd_reord(chat_id)
    return

def cmd_help(chat_id):
    u"""cmd_help: 봇 사용법 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    send_msg(chat_id, USAGE, keyboard=CUSTOM_KEYBOARD)

def cmd_view(chat_id):
    u"""cmd_view: 봇 수동 실행
    chat_id (integer) 채팅 ID
    """
    #s = CollectPrices(url_index)
    quote_list = extract_quote(chat_id)

    s = CollectIndex(url_index + 'KOSPI')
    s = s + CollectIndex(url_index + 'KOSDAQ')
    vtotal = 0
    ttotal = 0
    ytotal = 0
    for aaa in quote_list:
#        send_msg(chat_id, url_quote + aaa)
        temp = CollectPrices(url_quote + aaa[0])
        s += temp[0] + "\t" + temp[4] + "\t" + temp[5] + "\t" + format(aaa[1] * temp[1], ",") + "\n"
        vtotal += aaa[1] * temp[1]
        ttotal += aaa[1] * int(temp[2])
        ytotal += aaa[1] * int(temp[3])
#    s = s + CollectPrices(url_quote + '058470')
#    s = s + CollectPrices(url_quote + '042700')
#    s = s + CollectPrices(url_quote + '003650')
#    s = s + CollectPrices(url_quote + '026960')
#    s = s + CollectPrices(url_quote + '052330')
#    s = s + CollectPrices(url_quote + '036190')
#    s = s + CollectPrices(url_quote + '051360')
#    s = s + CollectPrices(url_quote + '114090')
#    s = s + CollectPrices(url_quote + '122630')
#    s = s + CollectPrices(url_quote + '114800')
#    요일 식별을 위한 테스트 목적으로 아래의 두 줄이 추가되었음
#    now = time.gmtime(time.time() + 3600 * 9)
#    s = s + str(now.tm_wday)
    vratio = vtotal / float(ytotal) * 100.0
    s = s + u'오늘의 변동금액은 ' + format(vtotal, ",") + u' 원 입니다.\n'
    s = s + u'현재 평가액은 ' + format(ttotal, ",") + u' 원 입니다.\n'
    s = s + u'현재 수익률은 ' + '{0:6.2f}'.format(vratio) + u'% 입니다.'
    send_msg(chat_id, s)

def cmd_reord(chat_id):
    set_status(chat_id, ST_REORD)

    #ReOrdKBD = extract_list(chat_id)

    sl = StockList.get_by_id(str(chat_id))
    sltemp = sl.info

    ReOrdKBD = []
    for aaa in sltemp:
        ReOrdKBD.append([aaa.stockname])
    ReOrdKBD.append([CMD_NONE])
    
    USER_KEYBOARD = ReOrdKBD
    send_msg(chat_id, u'재배치할 종목 이름을 입력(선택)하세요.', keyboard=USER_KEYBOARD)

def cmd_broadcast(chat_id, text):
    u"""cmd_broadcast: 봇이 활성화된 모든 채팅에 메시지 방송
    chat_id: (integer) 채팅 ID
    text:    (string)  방송할 메시지
    """
    send_msg(chat_id, u'메시지를 방송합니다.', keyboard=CUSTOM_KEYBOARD)
    broadcast(text)

def cmd_echo(chat_id, text, reply_to):
    u"""cmd_echo: 사용자의 메시지를 따라서 답장
    chat_id:  (integer) 채팅 ID
    text:     (string)  사용자가 보낸 메시지 내용
    reply_to: (integer) 답장할 메시지 ID
    """
    send_msg(chat_id, text, reply_to=reply_to)

def cron_method(handler):
    def check_if_cron(self, *args, **kwargs):
        if self.request.headers.get('X-AppEngine-Cron') is None:
            self.error(403)
        else:
            return handler(self, *args, **kwargs)
    return check_if_cron

def process_cmds(msg):
    u"""사용자 메시지를 분석해 봇 명령을 처리
    chat_id: (integer) 채팅 ID
    text:    (string)  사용자가 보낸 메시지 내용
    """
    msg_id = msg['message_id']
    chat_id = msg['chat']['id']
    text = msg.get('text')
    if (not text):
        return
    if CMD_START == text:
        cmd_start(chat_id)
        return
    if (not get_enabled(chat_id)):
        return
    if CMD_STOP == text:
        cmd_stop(chat_id)
        return
    if CMD_ADD == text:
        cmd_add(chat_id)
        return
    if CMD_DEL == text:
        cmd_del(chat_id)
        return
    if CMD_EDITP == text:
        cmd_editp(chat_id)
        return
    if CMD_EDITQ == text:
        cmd_editq(chat_id)
        return
    if CMD_LIST == text:
        cmd_list(chat_id)
        return
    if CMD_NONE == text:
        cmd_none(chat_id)
        return
    if CMD_VIEW == text:
        cmd_view(chat_id)
        return
    if CMD_REORD == text:
        cmd_reord(chat_id)
        return
    if CMD_HELP == text:
        cmd_help(chat_id)
        return
    if get_status(chat_id) == ST_ADD:
        result_list = FindCodeAPI(APIKey, text)
        if not result_list[0]:
            send_msg(chat_id, u'종목명을 검색할 수 없습니다. 다시 확인 후 입력해주세요.')
        elif len(result_list[0]) == 1 and result_list[0][0][0] == text:
            set_stocklist(chat_id, text, result_list[1][0][0])
            send_msg(chat_id, result_list[0][0][0] + u' 종목이 추가되었습니다.', keyboard=CUSTOM_KEYBOARD)
        else:
            count = 0
            for li in result_list[0]:
                if li[0] == text:
                    send_msg(chat_id, u'동일한 종목이 발견되었습니다.')
                    set_stocklist(chat_id, text, result_list[1][count][0])
                    send_msg(chat_id, text + u' 종목이 추가되었습니다.', keyboard=CUSTOM_KEYBOARD)
                    return
                count += 1
            merge_list = MergeList(result_list[0])
            result_list[0].append([CMD_NONE])
            cmd_addquote(chat_id, merge_list, result_list[0])
        return
    if get_status(chat_id) == ST_DEL:
        # NDB 에서 입력된 text 와 일치하는 종목명이 있는지 검색 : 목록에서 선택하기 때문에 생략 가능
        # get_by_id 로 클래스를 받은 후에 Structured Property 를 for loop 로 검색
        # 있으면 (확인 후)삭제 실행(cmd_delquote)
        # 삭제시에 모든 필드들을 함께 삭제해야 함
        # 없으면 없다는 메시지 출력
        cmd_delquote(chat_id, text)
        return
    if get_status(chat_id) == ST_EDITP:
        # 가격 수정을 위해서 종목입력이 된 다음 처리할 로직
        cmd_editprice(chat_id, text)
        return
    if get_status(chat_id) == ST_EDITP_VAL:
        cmd_editprice_val(chat_id, text)
        return
    if get_status(chat_id) == ST_EDITQ:
        # 수량 수정을 위해서 종목입력이 된 다음 처리할 로직
        cmd_editquantity(chat_id, text)
        return
    if get_status(chat_id) == ST_EDITQ_VAL:
        cmd_editquantity_val(chat_id, text)
        return
    if get_status(chat_id) == ST_REORD:
        cmd_reord_rank(chat_id, text)
        return
    if get_status(chat_id) == ST_REORD_RANK:
        cmd_reord_execute(chat_id, text)
        return
    cmd_broadcast_match = re.match('^' + CMD_BROADCAST + ' (.*)', text)
    if cmd_broadcast_match:
        cmd_broadcast(chat_id, cmd_broadcast_match.group(1))
        return
    cmd_echo(chat_id, text, reply_to=msg_id)
    return

# 웹 요청에 대한 핸들러 정의
# /me 요청시
class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))

# /updates 요청시
class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))

# /set-wehook 요청시
class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

# /webhook 요청시 (텔레그램 봇 API)
class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        self.response.write(json.dumps(body))
        process_cmds(body['message'])

class WebhookHandler1(webapp2.RequestHandler):
    @cron_method
    def get(self):
        now = time.gmtime(time.time() + 3600 * 9)
        # 토요일이나 일요일인 경우엔 알림 중지
        if now.tm_wday == 5 or now.tm_wday == 6:
            return
        else:
            urlfetch.set_default_fetch_deadline(60)
            s = CollectIndex(url_index + "KOSPI")
            s = s + CollectIndex(url_index + "KOSDAQ")
#            s = s + CollectPrices(url_quote + '058470')
#            s = s + CollectPrices(url_quote + '042700')
#            s = s + CollectPrices(url_quote + '003650')
#            s = s + CollectPrices(url_quote + '026960')
#            s = s + CollectPrices(url_quote + '052330')
#            s = s + CollectPrices(url_quote + '036190')
#            s = s + CollectPrices(url_quote + '051360')
#            s = s + CollectPrices(url_quote + '114090')
#            s = s + CollectPrices(url_quote + '122630')
#            s = s + CollectPrices(url_quote + '114800')
            broadcast(s)
#        broadcast('Test Message')

# 구글 앱 엔진에 웹 요청 핸들러 지정
app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set-webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/broadcast-news', WebhookHandler1),
], debug=True)
