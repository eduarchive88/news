import feedparser
import datetime
from datetime import timedelta, timezone
import re
import trafilatura
import os

# ---------------------------------------------------------
# 1. 한국 시간(KST) 설정 (GitHub 서버 시간 보정용)
# ---------------------------------------------------------
KST = timezone(timedelta(hours=9))

def get_korea_time():
    """현재 한국 시간을 반환하는 함수"""
    return datetime.datetime.now(KST)

# ---------------------------------------------------------
# 2. 뉴스 본문 추출 및 정제 함수 (Trafilatura 활용)
# ---------------------------------------------------------
def get_clean_summary(url):
    try:
        # 본문 다운로드 (User-Agent 자동 위장으로 차단 방지)
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded is None:
            return None

        # 본문 텍스트 추출
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        
        if not text or len(text) < 50:
            return None

        # 텍스트 정제 (불필요한 공백 및 줄바꿈 제거)
        text = text.replace('\n', ' ').strip()
        text = re.sub(r'\s+', ' ', text)

        # 문장 단위로 분리하여 요약 생성 (최대 300자)
        sentences = text.split('. ')
        summary_sentences = []
        char_count = 0
        
        for sent in sentences:
            clean_sent = sent.strip()
            if len(clean_sent) < 20: continue # 너무 짧은 문장 제외
            
            if not clean_sent.endswith('.'):
                clean_sent += '.'
            
            summary_sentences.append(clean_sent)
            char_count += len(clean_sent)
            
            if char_count > 350: # 요약 길이 제한 (약 3~4문장)
                break
        
        return ' '.join(summary_sentences) if summary_sentences else None

    except Exception as e:
        print(f"⚠️ 요약 실패 ({url}): {e}")
        return None

# ---------------------------------------------------------
# 3. 뉴스 수집 및 마크다운 생성 메인 함수
# ---------------------------------------------------------
def fetch_news():
    # 신뢰도 높은 뉴스 소스 목록 (필요시 수정 가능)
    sources = {
        "🤖 인공지능 (AI)": "http://www.aitimes.com/rss/allArticle.xml",
        "💰 경제": "https://www.hankyung.com/feed/economy", 
        "🎓 교육": "http://www.veritas-a.com/rss/allArticle.xml" 
    }
    
    now = get_korea_time()
    today_str = now.strftime("%Y-%m-%d")
    
    # 오전/오후 구분 로직
    time_tag = "오전" if now.hour < 12 else "오후"
    
    # 옵시디언용 Frontmatter 작성
    markdown = f"""---
date: {today_str}
time: {now.strftime("%H:%M:%S")}
type: news_briefing
tags: [뉴스, {time_tag}, 자동화]
created_at: {now.strftime("%Y-%m-%d %H:%M:%S")}
---

# 📅 {now.strftime('%Y년 %m월 %d일')} {time_tag} 뉴스 브리핑

"""
    
    # 각 카테고리별 뉴스 수집 시작
    for category, rss_url in sources.items():
        markdown += f"## {category}\n"
        print(f"🔍 [{category}] 뉴스 수집 중...")
        
        try:
            feed = feedparser.parse(rss_url)
            success_count = 0
            
            for entry in feed.entries:
                if success_count >= 3: break # 카테고리당 최대 3개 기사만
                
                print(f"  - 분석 중: {entry.title}...")
                
                # 본문 요약 시도
                summary = get_clean_summary(entry.link)
                
                # 본문 추출 실패 시 RSS 기본 요약(description) 사용
                if not summary:
                    summary = entry.get('description', '')[:100] + "..." if 'description' in entry else "요약 정보를 불러올 수 없습니다."
                    summary = re.sub(r'<[^>]+>', '', summary) # HTML 태그 제거
                
                # 마크다운에 추가
                markdown += f"### 🔗 [{entry.title}]({entry.link})\n"
                markdown += f"> {summary}\n\n"
                success_count += 1
                
        except Exception as e:
            markdown += f"> ⚠️ 뉴스를 가져오는 중 오류가 발생했습니다: {e}\n\n"

    markdown += "---\n"
    markdown += f"✅ **최종 업데이트(한국시간):** {now.strftime('%Y-%m-%d %H:%M:%S')}\n"

    # 파일명 생성 (예: 2026-01-27_오후_Daily_News.md)
    # 구체적인 시간(시/분)을 원하시면 아래 주석을 해제하고 사용하세요
    # filename = f"{today_str}_{time_tag}_{now.strftime('%I시_%M분')}_News.md"
    filename = f"{today_str}_{time_tag}_Daily_News_Briefing.md"
    
    return filename, markdown

# ---------------------------------------------------------
# 4. 실행 및 파일 저장
# ---------------------------------------------------------
if __name__ == "__main__":
    filename, content = fetch_news()
    
    # GitHub Actions 환경에서 실행될 때 파일 저장
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"\n🎉 파일 생성 완료: {filename}")
