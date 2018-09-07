import time
from urllib.request import urlopen
from bs4 import BeautifulSoup

from newspaper import Article
from konlpy.tag import Twitter
from collections import Counter
import matplotlib.pyplot as plt
import pytagcloud


DELAY = 1
URL_PREFIX = 'http://finance.naver.com'


def getArticles(page):
    "아티클들을 수집"
    url = 'http://finance.naver.com/news/market_special.nhn?&page=%d'%page
    print('try to crawl:', url)
    articles = []

    time.sleep(DELAY)
    content = urlopen(url)
    soup = BeautifulSoup(content, 'html5lib')
    for tr in soup.select('div.boardList2 tr'):
        try:
            a = tr.select('a')
            href = a[0].get('href')
            title = a[0].get('title')
            td = tr.select('td.wdate')
            date = td[0].text
        except:
            continue
        else:
            articles.append( (href, title, date) )
    return articles

def getContent(href):
    url = URL_PREFIX + href
    print('try to crawl:', url)

    a = Article(url, language='ko')
    a.download()
    a.parse()

    # print(a.title)
    # print(a.text)

    time.sleep(DELAY)

    return a.text

if __name__ == "__main__":
    print('''네이버 금융 장중특징주 뉴스기사를 crawling 합니다.''')

    # init page
    page = 1
    news_text = ''

    # 하루에 한번만 돌리는 걸 가정하고, 몇 페이지만 가져올까?
    # 5 페이지면 대강 하루치 정도 됨.
    while page<=5:
        #글목록에서 뉴스들 수집
        articles = getArticles(page)
        alreadyInserted = 0
        success = 0

        for a in articles:
            href, title, date = a[0], a[1], a[2]
            # 해당 url에 들어가서 content 킵
            news_text += getContent(href)

        page += 1


    # 명사추출, 1글자는 단어는 무시
    pos = Twitter() 
    nouns = pos.nouns(news_text)
    nouns = [n for n in nouns if len(n) > 1]

    # 가장 많이 등장한 단어(명사) 몇개 킵?
    count = Counter(nouns)
    tags = count.most_common(150)

    # make & save WordCloud
    taglist = pytagcloud.make_tags(tags, maxsize=120)
    # 그냥 쓰면 한글이 깨지므로,
    # 한글폰트를 다운받아서 pytagcloud/fonts/fonts.json에 다음과 같이 추가.
    # {
    #     "name": "Korean",
    #     "ttf": "NanumGothic.ttf",
    #     "web": "http://fonts.googleapis.com/earlyaccess/nanumgothic.css"
    # },
    pytagcloud.create_tag_image(taglist, 'wordcloud.png', fontname='Korean', size=(1200, 800))