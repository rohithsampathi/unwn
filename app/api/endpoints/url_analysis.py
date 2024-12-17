# app/services/url_service.py
from newspaper import Article
import asyncio
from typing import Dict
from datetime import datetime

class URLService:
    @staticmethod
    async def extract_content(url: str) -> Dict:
        article = Article(url)
        await asyncio.to_thread(article.download)
        await asyncio.to_thread(article.parse)
        return {
            "title": article.title,
            "content": article.text,
            "timestamp": int(datetime.now().timestamp())
        }