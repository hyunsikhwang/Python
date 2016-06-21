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

\n
문제점

	1) Google App Engine 에서 전체 종목 parsing 해서 bot 을 통해 broadcast 하는데 25~30초 정도 걸림 (parse_1.py)
	2) parse_1_nv.py 의 방식을 이용해서 필요한 종목의 정보만 가져올 경우 5초 이내로 런타임 단축

\n
향후계획

	1) 조회 대상 종목을 명령어를 이용해서 NDB 에 추가 및 삭제 (사용자별)
	2) 등록 종목별 목표수익률과 매수평단가 입력받아서 현재 가격이 목표수익률 도달시 알림
	3) 전체 종목명 / 종목코드를 "/init" 명령을 이용해서 저장 및 refresh
