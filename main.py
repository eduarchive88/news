def fetch_news():
    # 분야별로 신뢰도 높은 서로 다른 언론사 RSS를 지정합니다.
    feeds = {
        "인공지능(AI)": "http://www.aitimes.com/rss/allArticle.xml", # AI 전문지
        "교육": "https://www.edunews.co.kr/rss/allArticle.xml",     # 교육 전문지
        "정치/사회": "https://www.yna.co.kr/rss/news.xml"           # 연합뉴스 속보
    }
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    today_with_day = datetime.datetime.now().strftime("%Y-%m-%d(%a)")
    
    content = f"""---
date: {today_str}
type: insight
tags: [AI, 교육, 정치, 사회]
---

# 📅 {today_with_day} 분야별 종합 뉴스 브리핑

"""

    brief_summary = ""

    for category, url in feeds.items():
        feed = feedparser.parse(url)
        # 피드 연결 실패 시 건너뛰기
        if not feed.entries:
            continue
            
        content += f"## 📌 {category} 분야\n"
        
        for i, entry in enumerate(feed.entries[:3]):
            # HTML 태그 제거
            summary = re.sub('<[^<]+?>', '', entry.description) if 'description' in entry else "내용은 링크를 참조하세요."
            # 요약 내용이 너무 길면 자르기
            summary = summary.strip()[:150] + "..." if len(summary) > 150 else summary
            
            content += f"### {entry.title}\n"
            content += f"- **핵심내용:** {summary}\n"
            content += f"- [기사 원문 보기]({entry.link})\n\n"
            
            # 파일 제목용 요약 (첫 번째 분야의 첫 번째 기사 제목)
            if not brief_summary:
                brief_summary = re.sub(r'[\\/:*?"<>|]', '', entry.title)[:20]

    filename = f"{today_str} {brief_summary}.md"
    return filename, content
