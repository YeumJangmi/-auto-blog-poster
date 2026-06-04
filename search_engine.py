import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime, timedelta, timezone
import email.utils

def search_news(topic: str, target_date=None, max_results: int = 3):
    """
    Search for latest news using Google News RSS.
    Returns a list of dictionaries with 'title', 'snippet', 'url'.
    target_date should be a datetime.date object. If None, it defaults to today.
    """
    results = []
    
    # 구글 뉴스 RSS URL (한국어)
    encoded_topic = urllib.parse.quote(topic)
    rss_url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        # 뉴스 RSS 데이터 가져오기
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # XML 파싱
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        
        if target_date is None:
            target_date = now.date()
        
        for item in items:
            pubDate = item.pubDate.text if item.pubDate else ""
            
            # 오늘 또는 어제 발행된 기사인지 확인
            is_valid_date = False
            if pubDate:
                try:
                    dt_tuple = email.utils.parsedate_tz(pubDate)
                    if dt_tuple:
                        dt = datetime.fromtimestamp(email.utils.mktime_tz(dt_tuple), timezone.utc)
                        dt_kst = dt.astimezone(kst)
                        if dt_kst.date() == target_date:
                            is_valid_date = True
                except Exception:
                    pass
            
            if not is_valid_date:
                continue

            title = item.title.text if item.title else ""
            link = item.link.text if item.link else ""
            source = item.source.text if item.source else "Google News"
            
            results.append({
                'title': title,
                'snippet': f"발행일: {pubDate} (뉴스 기사입니다. 제목을 바탕으로 유추하세요.)", 
                'url': link,
                'source': source,
                'date': pubDate
            })
            
            if len(results) >= max_results:
                break
            
    except Exception as e:
        print(f"[{topic}] 검색 중 오류 발생: {e}")
        
    return results
