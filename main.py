#-*- coding: utf-8 -*-
#
# original:    https://github.com/yukuku/telebot
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

# 파싱 관련 라이브러리 로드
import urllib2
from bs4 import BeautifulSoup
import time
import pprint

import unicodedata

# 파싱 주소
url_quote = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:"  # 종목 시세 주소
url_index = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_INDEX:" # 인덱스 조회 주소
url_quotelist_KSP = "http://finance.daum.net/quote/all.daum?type=S&stype=P"  #type : U(업종순), S(가나다순)
url_quotelist_KSD = "http://finance.daum.net/quote/all.daum?type=S&stype=Q"  #stype : P(유가증권), Q(코스닥)


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
    price_ud = (price_t - price_y) / float(price_y) * 100.0
    price_t = format(price_t, ",")
    return u"{0} {1:8} {2:8} {3:.2f}%\n".format(preformat_cjk(name, 14, "<", "_"), quote, price_t, price_ud)


# 봇 토큰, 봇 API 주소
TOKEN = '234646277:AAEl5x5nIIgu36YtQWGqJR6pLdB_0bGNUvM'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

# 봇이 응답할 명령어
CMD_START     = '/start'
CMD_STOP      = '/stop'
CMD_ADD       = '/add'
CMD_DEL       = '/del'
CMD_NONE      = '/none'
CMD_HELP      = '/help'
CMD_VIEW      = '/view'
CMD_BROADCAST = '/broadcast'

# 봇 사용법 & 메시지
USAGE = u"""[사용법] 아래 명령어를 메시지로 보내거나 버튼을 누르시면 됩니다.
/start - (로봇 활성화)
/stop  - (로봇 비활성화)
/add   - (종목 추가)
/del   - (종목 삭제)
/none  - (종목 추가/삭제 종료)
/view  - (수동 실행)
/help  - (이 도움말 보여주기)
"""
MSG_START = u'봇을 시작합니다.'
MSG_STOP  = u'봇을 정지합니다.'

# 커스텀 키보드
CUSTOM_KEYBOARD = [
        [CMD_START, CMD_STOP],
        [CMD_ADD, CMD_DEL, CMD_NONE],
        [CMD_VIEW, CMD_HELP],
        ]

ST_ECHO, ST_ADD, ST_DEL = range(3)

# 채팅별 로봇 활성화 상태
# 구글 앱 엔진의 Datastore(NDB)에 상태를 저장하고 읽음
# 사용자가 /start 누르면 활성화
# 사용자가 /stop  누르면 비활성화
# 사용자가 /add   누르면 종목 추가 모드 진입
# 사용자가 /del   누르면 종목 삭제 모드 진입
# 사용자가 /none  누르면 종목 추가/삭제모드 종료
class EnableStatus(ndb.Model):
    enabled = ndb.BooleanProperty(required=True, indexed=True, default=False,)

class CommandStatus(ndb.Model):
    command_status = ndb.IntegerProperty(required=True, indexed=True, default=False,)

class QuoteList(ndb.Model):
    quote_code = ndb.StringProperty(required=True, indexed=True, default=False,)
    quote_name = ndb.StringProperty(required=True, indexed=True, default=False,)

class CompList(ndb.Model):
    comp_code = ndb.StringProperty(required=True, indexed=True, default=False,)
    comp_name = ndb.StringProperty(required=True, indexed=True, default=False,)

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
    chat_id:    (integer) 봇을 활성화/비활성화할 채팅 ID
    cmd_status: (integer) 명령어 상태(add/del)
    """
    cs = CommandStatus.get_or_insert(str(chat_id))
    cs.command_status = cmd_status
    cs.put()

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
def send_msg(chat_id, text, reply_to=None, no_preview=True, keyboard=None):
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
            'one_time_keyboard': False,
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
    send_msg(chat_id, u'추가할 종목 코드를 입력하세요.')
    
def cmd_del(chat_id):
    u"""cmd_del: 종목 삭제 모드
    chat_id: (integer) 채팅 ID
    """
    set_status(chat_id, ST_DEL)
    send_msg(chat_id, u'삭제할 종목 코드를 입력하세요.')

def cmd_none(chat_id):
    u"""cmd_none: 종목 추가/삭제 모드 종료
    chat_id: (integer) 채팅 ID
    """
    set_status(chat_id, ST_ECHO)
    send_msg(chat_id, u'종목 추가/삭제가 종료되었습니다.')

def cmd_addquote(chat_id, text):
    u"""cmd_addquote: 종목 추가
    chat_id: (integer) 채팅 ID
    """
    send_msg(chat_id, text + u' 종목이 추가되었습니다.')

def cmd_delquote(chat_id, text):
    u"""cmd_delquote: 종목 삭제
    chat_id: (integer) 채팅 ID
    """
    send_msg(chat_id, text + u' 종목이 삭제되었습니다.')

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
    s = CollectIndex(url_index + 'KOSPI')
    s = s + CollectIndex(url_index + 'KOSDAQ')
    s = s + CollectPrices(url_quote + '058470')
    s = s + CollectPrices(url_quote + '042700')
    s = s + CollectPrices(url_quote + '003650')
    s = s + CollectPrices(url_quote + '026960')
    s = s + CollectPrices(url_quote + '052330')
    s = s + CollectPrices(url_quote + '036190')
    s = s + CollectPrices(url_quote + '051360')
    s = s + CollectPrices(url_quote + '114090')
    s = s + CollectPrices(url_quote + '122630')
    s = s + CollectPrices(url_quote + '114800')
    send_msg(chat_id, s)

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
    if CMD_NONE == text:
        cmd_none(chat_id)
        return
    if CMD_VIEW == text:
        cmd_view(chat_id)
        return
    if CMD_HELP == text:
        cmd_help(chat_id)
        return
    if get_status(chat_id) == ST_ADD:
        cmd_addquote(chat_id, text)
        return
    if get_status(chat_id) == ST_DEL:
        cmd_delquote(chat_id, text)
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
        now = time.localtime()
#        if now.tm_wday == 5 or now.tw_wday == 6:
#            return
#        else:
        urlfetch.set_default_fetch_deadline(60)
        s = CollectIndex(url_index + "KOSPI")
        s = s + CollectIndex(url_index + "KOSDAQ")
        s = s + CollectPrices(url_quote + '058470')
        s = s + CollectPrices(url_quote + '042700')
        s = s + CollectPrices(url_quote + '003650')
        s = s + CollectPrices(url_quote + '026960')
        s = s + CollectPrices(url_quote + '052330')
        s = s + CollectPrices(url_quote + '036190')
        s = s + CollectPrices(url_quote + '051360')
        s = s + CollectPrices(url_quote + '114090')
        s = s + CollectPrices(url_quote + '122630')
        s = s + CollectPrices(url_quote + '114800')
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
