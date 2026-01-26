import feedparser
import datetime
import re
import trafilatura # newspaper3k 대신 사용 (더 강력한 본문 추출기)

def get_clean_summary(url):
    """
    trafilatura를 사용하여 기사 본문을 추출하고 요약합니다.
    """
    try:
        # 1. trafilatura로 다운로드 및 본문 추출
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded is None:
            return ""

        # include_comments=False로 댓글/광고 제거, formatting=True로 구조 유지
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False, no_fallback=False)
        
        if not text or len(text) < 50:
            return ""

        # 2. 텍스트 정제 (줄바꿈을 공백으로)
        text = text.replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)

        # 3. 문장 단위 분리 (간이 로직)
        sentences = text.split('. ')
        
        summary_sentences = []
        char_count = 0
        
        for sent in sentences:
            clean_sent = sent.strip()
            if not clean_sent: continue
            
            # 너무 짧은 문장(기자 이메일, 포토뉴스 설명 등) 건너뛰기
            if len(clean_sent) < 20: continue
            
            # 문장 끝 마침표 보정
            if not clean_sent.endswith('.'):
                clean_sent += '.'
            
            summary_sentences.append(clean_sent)
            char_count += len(clean_sent)
            
            # 약 350자 내외에서 끊기
            if char_count > 350:
                break
        
        # 문장이 너무 적으면(1문장 미만) 요약 실패로 간주
        if not summary_sentences:
            return ""

        return ' '.join(summary_sentences)

    except Exception as e:
        # 로그에 에러를 남겨 디버깅 용이하게 함
        print(f"[Error] Failed to summarize {url}: {e}")
        return ""

def fetch_news():
    # RSS 소스 최적화
    sources = {
        "🤖 인공지능 (AI)": "http://www.aitimes.com/rss/allArticle.xml",
        # 매일경제 종합 대신 '한국경제(한경) 경제 섹션'으로 변경 (날씨/연예 배제)
        "💰 경제": "https://www.hankyung.com/feed/economy", 
        # 동아일보 교육 섹션 (trafilatura로 추출 시도)
        "🎓 교육": "https://rss.donga.com/education.php" 
    }
    
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    update_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    markdown = f"""---
date: {today_str}
last_update: {update_time}
type: insight
topic: [인공지능, 경제, 교육]
tags: [뉴스, 요약, {today_str}]
source: [AI타임스, 한국경제, 동아일보]
---

# 📅 {now.strftime('%Y년 %m월 %d일(%a)')} 핵심 뉴스 브리핑

"""
    
    first_title = "" 

    for category, rss_url in sources.items():
        markdown += f"## {category}\n"
        print(f"Processing Category: {category}...") # 진행상황 출력
        
        try:
            feed = feedparser.parse(rss_url)
            success_count = 0
            
            for entry in feed.entries:
                if success_count >= 2: break
                
                print(f" - Trying: {entry.title}") # 어떤 기사를 시도하는지 출력
                summary = get_clean_summary(entry.link)
                
                if not summary:
                    print("   -> Fail (Content empty or too short)")
                    continue
                
                print("   -> Success!")
                markdown += f"### 🔗 [{entry.title}]({entry.link})\n"
                markdown += f"> {summary}\n\n"
                
                # 파일명 생성을 위한 첫 번째 기사 제목 추출
                if not first_title:
                    clean_title = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', entry.title).strip()
                    first_title = clean_title.replace(" ", "_")[:15]
                
                success_count += 1
                
        except Exception as e:
            print(f"Error in category {category}: {e}")

    markdown += "---\n"
    markdown += f"### 📂 자동화 기록 안내\n"
    markdown += f"최종 업데이트 시각: **{update_time}**\n"
    
    # 제목이 없을 경우를 대비한 기본값
    if not first_title:
        first_title = "News_Briefing"

    filename = f"{today_str}_{first_title}.md"
    return filename, markdown

if __name__ == "__main__":
    filename, content = fetch_news()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {filename}")
