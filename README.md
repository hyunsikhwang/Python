# python

1. main.py

	1) Telegram Bot 기능을 이용해서 일정시간마다 자동 알림
	
	2) 시장 인덱스(KOSPI, KOSDAQ) 실시간 정보 제공
	
  	3) 등록된 보유 종목의 실시간 주가를 봇 등록자에게 정해진 시간마다 전송(cron.yaml 에서 설정, 오전 9시부터 15시 30분까지 매 30분 주기. 장시작과 장종료 직후는 1분 단위로 3회)
	
	4) /view 명령으로 수시로 호출 가능
	
	5) /eq 명령으로 보유주식수 등록
	
	6) /reord 명령으로 등록된 보유주식 순서 변경
	
	7) 오늘의 포트폴리오 변동금액 / 실시간 평가액 / 당일 수익률(%) / 포트폴리오 PER & PBR 정보 제공
	
	8) 등록된 보유 종목의 당일 수익률 / PER / PBR 정보 제공 (EPS, BPS 는 최근 결산기준)
	
	
	
2. parse.py : Daum 전종목 주가 정보에서 전체 정보 parsing (종목명, 종목번호, 현재주가, 등락폭)
 

3. parse_1.py : Daum 종목별 주가 정보에서 종목별 parsing


4. parse_1_nv.py : 네이버 종목별 주가 정보에서 종목별 parsing


5. parse_div.py : 최근 주당 배당금 정보를 parsing



기타 : python 2.7 기준


문제점

	1) Google App Engine 에서 전체 종목 parsing 해서 bot 을 통해 broadcast 하는데 25~30초 정도 걸림 (parse_1.py)
	2) parse_1_nv.py 의 방식을 이용해서 필요한 종목의 정보만 가져올 경우 5초 이내로 런타임 단축


향후계획

	1) 실적공시 일정 기준 이상 기업 실시간 알림
	2) 인터넷상의 재무/투자정보 연동
	


Reference

	1) http://bakyeono.net/post/2015-08-24-using-telegram-bot-api.html
	2) http://blog.gman.io/entry/%EC%8B%A4%EC%8B%9C%EA%B0%84-%EB%84%A4%EC%9D%B4%EB%B2%84-%EC%A3%BC%EC%8B%9D-%EC%8B%9C%EC%84%B8-xml
	3) https://opentutorials.org/course/811/3473
	4) http://gnoownow10.cafe24.com/cjk-formatting.html
	5) http://egloos.zum.com/mcchae/v/11076302
