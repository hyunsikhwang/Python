# python

1. main.py

	1) Telegram Bot 기능을 이용해서 일정시간마다 자동 알림

	2) BeautifulSoup 을 이용하여 실시간 주가 정보(다음)를 파싱해서 전체 종목(유가증권, 코스탁)에 대한 종목명/종목번호/현재가/등락률 정보를 dictionary 형태로 저장
  
	3) 특정 종목의 실시간 주가를 전체 봇 등록자에게 정해진 시간마다 전송(cron.yaml 에서 설정, 오전 9시부터 15시까지 매 30분 주기)

	4) /view 명령으로 수시로 호출 가능
	
	
	
2. parse.py : Daum 전종목 주가 정보에서 전체 정보 parsing (종목명, 종목번호, 현재주가, 등락폭)
 

3. parse_1.py : Daum 종목별 주가 정보에서 종목별 parsing


4. parse_1_nv.py : 네이버 종목별 주가 정보에서 종목별 parsing


기타 : python 2.7 기준


문제점 : Google App Engine 에서 전체 종목 parsing 해서 bot 을 통해 broadcast 하는데 25~30초 정도 걸림

