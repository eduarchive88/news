import feedparser
import datetime
import re
import os
from newspaper import Article

def get_article_content(url):
    try:
        article = Article(url, language='ko')
        article.download()
        article.parse()
        text = re.sub(r'\n+', ' ', article.text.strip())
        summary = text[:350]
        if "." in summary[300:]:
            summary = summary[:300] + summary[300:].split('.')[0] + "."
        else:
            summary += "..."
        return summary
    except:
        return ""

def fetch_korean_news():
    sources = {
        "🤖 인공지능 (AI)": "http://www.aitimes.com/rss/allArticle.xml", 
        "🏛️ 정치": "https://www.yna.co.kr/rss/politics.xml", 
        "🏥 사회": "https://www.yna.co.kr/rss/society.xml",
        "🎓 교육": "https://www.yna.co.kr/rss/society-education.xml" # 안정적인 교육 소스
    }
    
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    # 초 단위까지 포함하여 내용 중복 방지
    update_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    markdown = f"---\ndate: {today_str}\nlast_update: {update_time}\ntags: [뉴스, 스크랩]\n---\n\n"
    markdown += f"# 📅 {now.strftime('%Y년 %m월 %d일(%a)')} 핵심 뉴스 브리핑\n\n"
    
    first_title = "" 

    for category, rss_url in sources.items():
        markdown += f"## {category}\n"
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:2]:
                content_summary = get_article_content(entry.link)
                if not content_summary:
                    content_summary = re.sub('<[^<]+?>', '', entry.description)[:200] + "..."
                
                markdown += f"### 🔗 [{entry.title}]({entry.link})\n"
                markdown += f"> {content_summary}\n\n"

                # (기존 코드의 first_title 생성 부분을 아래로 교체)
                if not first_title:
                    # 1. 특수문자 제거 (공백은 유지)
                    clean_title = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', entry.title).strip()
                    # 2. 공백을 언더바(_)로 치환하고 15자까지만 자름
                    safe_title = clean_title.replace(" ", "_")[:15]
                    first_title = safe_title
        except:
            markdown += "뉴스를 불러오는 중 오류가 발생했습니다.\n\n"

    markdown += "---\n"
    markdown += f"### 📂 자동화 기록 안내\n"
    markdown += f"최종 업데이트 시각: **{update_time}**\n" # 매번 내용이 바뀌게 됨
    
    filename = f"{today_str}_{first_title}.md"
    return filename, markdown

if __name__ == "__main__":
    filename, content = fetch_korean_news()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
