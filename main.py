import feedparser
import datetime
import os

def fetch_news():
    # 경제 뉴스 RSS 피드 (예: 매일경제)
    rss_url = "https://www.mk.co.kr/rss/30100041/" 
    feed = feedparser.parse(rss_url)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    content = f"---\ndate: {today}\ntags: [경제, 뉴스, 자동화]\n---\n\n# 📅 {today} 경제 뉴스 브리핑\n\n"
    
    for entry in feed.entries[:10]: # 최신 뉴스 10개
        content += f"### 📌 {entry.title}\n"
        content += f"- **요약:** {entry.description if 'description' in entry else '링크 참조'}\n"
        content += f"- [기사 원문 보기]({entry.link})\n\n"
        
    return today, content

def save_to_file(today, content):
    filename = f"{today}-economy-summary.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

if __name__ == "__main__":
    today, content = fetch_news()
    save_to_file(today, content)
    print(f"File created successfully: {today}")
