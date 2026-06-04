import requests
import urllib.parse
from datetime import datetime, timedelta, timezone
import email.utils
import os
import re

def search_news(topic: str, target_date=None, max_results: int = 3):
    """
    Search for latest news using Naver Open API (News).
    Returns a list of dictionaries with 'title', 'snippet', 'url'.
    target_date should be a datetime.date object. If None, it defaults to today.
    """
    results = []
    
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("네이버 API 키가 설정되지 않았습니다 (.env 파일을 확인하세요).")
        return []
    
    # 네이버 뉴스 검색 API URL (정확도 순 대신 최신순(date)으로 설정)
    encoded_topic = urllib.parse.quote(topic)
    api_url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_topic}&display=10&sort=date"
    
    try:
        headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])
        
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        
        if target_date is None:
            target_date = now.date()
            
        def clean_html(raw_html):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            # 네이버 API는 예약어들을 &quot; &lt; &gt; &amp; 등 이스케이프해서 주기도 함
            import html
            return html.unescape(cleantext)
        
        for item in items:
            pubDate = item.get('pubDate', "")
            
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

            title = clean_html(item.get('title', ""))
            snippet_raw = clean_html(item.get('description', ""))
            link = item.get('link', "")
            
            results.append({
                'title': title,
                'snippet': f"발행일: {pubDate} / 내용 요약: {snippet_raw}", 
                'url': link,
                'source': "네이버 뉴스",
                'date': pubDate
            })
            
            if len(results) >= max_results:
                break
            
    except Exception as e:
        print(f"[{topic}] 검색 중 오류 발생: {e}")
        
    return results
