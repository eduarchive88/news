import datetime
import re
import requests
from bs4 import BeautifulSoup
import trafilatura

def get_clean_summary(url):
    try:
        # 뉴스 본문 추출을 위한 최적 설정
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None: return ""

        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        if not text or len(text) < 100: return ""

        # 불필요한 공백 및 줄바꿈 정제
        text = re.sub(r'\s+', ' ', text).strip()

        # 문장 단위 추출 및 요약
        sentences = text.split('. ')
        summary_sentences = []
        char_count = 0
        
        for sent in sentences:
            clean_sent = sent.strip()
            if len(clean_sent) < 25: continue # 너무 짧은 문장 제외
            if not clean_sent.endswith('.'): clean_sent += '.'
            
            summary_sentences.append(clean_sent)
            char_count += len(clean_sent)
            if char_count > 350: break # 핵심 내용 위주 요약
        
        return ' '.join(summary_sentences)
    except:
        return ""

def get_naver_section_links(sid1, sid2=None):
    """
    네이버 뉴스 섹션에서 리디렉션 없는 직접 기사 링크를 추출합니다.
    sid1: 105(IT), 101(경제), 102(사회)
    sid2: 250(교육)
    """
    links = []
    url = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={sid1}"
    if sid2:
        url += f"&sid2={sid2}"
        
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 기사 링크 패턴(n.news.naver.com) 탐색
        for a in soup.select('a[href*="article"]'):
            href = a['href']
            if 'n.news.naver.com/mnews/article/' in href:
                full_url = href.split('?')[0]
                if full_url not in links:
                    links.append(full_url)
            if len(links) >= 5: break 
    except Exception as e:
        print(f"Scraping Error: {e}")
    
    return links

def fetch_news():
    # 교육(sid2: 250) 섹션을 명확히 지정하여 누락 방지
    sections = {
        "🤖 인공지능 (AI)": {"sid1": "105"},
        "💰 경제": {"sid1": "101"},
        "🎓 교육": {"sid1": "102", "sid2": "250"}
    }
    
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    markdown = f"""---
date: {today_str}
last_update: {now.strftime("%Y-%m-%d %H:%M:%S")}
type: insight
topic: [인공지능, 경제, 교육]
---

# 📅 {now.strftime('%Y년 %m월 %d일(%a)')} 핵심 뉴스 브리핑

"""
    
    for category, ids in sections.items():
        markdown += f"## {category}\n"
        links = get_naver_section_links(ids['sid1'], ids.get('sid2'))
        success_count = 0
        
        for link in links:
            if success_count >= 2: break
            summary = get_clean_summary(link)
            if not summary: continue
            
            markdown += f"### 🔗 [기사 원문 확인하기]({link})\n"
            markdown += f"> {summary}\n\n"
            success_count += 1
            
        if success_count == 0:
            markdown += "> 해당 분야의 최신 뉴스를 불러오지 못했습니다.\n\n"

    filename = f"{today_str}_Daily_News_Briefing.md"
    return filename, markdown

if __name__ == "__main__":
    filename, content = fetch_news()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
