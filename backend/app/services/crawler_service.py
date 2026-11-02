import re
import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

class CrawlerService:
    @staticmethod
    async def fetch_and_clean_url(url: str) -> dict:
        """抓取并清洗微信公众号文章或通用网页内容"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"无法访问该网页，状态码: {resp.status_code}")
                html = resp.text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"抓取网页失败: {str(e)}")

        soup = BeautifulSoup(html, "html.parser")

        # 1. 提取标题
        title = ""
        # 微信公众号特有标题选择器
        wx_title = soup.find("h1", class_="rich_media_title") or soup.find(id="activity-name")
        if wx_title:
            title = wx_title.get_text(strip=True)
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)
        elif soup.title:
            title = soup.title.get_text(strip=True)
        else:
            title = "未知标题"

        # 2. 提取正文
        content_text = ""
        # 微信公众号特有正文容器
        wx_content = soup.find("div", class_="rich_media_content") or soup.find(id="js_content")
        if wx_content:
            # 清理无用标签
            for s in wx_content.find_all(["script", "style", "iframe"]):
                s.decompose()
            content_text = wx_content.get_text(separator="\n", strip=True)
        else:
            # 通用网页正文提取
            article_tag = soup.find("article") or soup.find("main") or soup.find("body")
            if article_tag:
                for s in article_tag.find_all(["script", "style", "nav", "footer", "header"]):
                    s.decompose()
                content_text = article_tag.get_text(separator="\n", strip=True)

        # 压缩多余连续空行
        cleaned_content = re.sub(r'\n{3,}', '\n\n', content_text).strip()
        
        # 截取前 4000 字符防止溢出，并提取前 200 字符作为简述
        summary = cleaned_content[:200].replace("\n", " ") + "..." if len(cleaned_content) > 200 else cleaned_content

        return {
            "title": title,
            "clean_content": cleaned_content[:5000],
            "summary": summary
        }
