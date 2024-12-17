# app/services/anthropic.py
import anthropic
from app.core.config import settings
from typing import Dict

class AnthropicService:
    def __init__(self):
        self.client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)

    async def get_elon_analysis(self, content: str) -> str:
        response = await anthropic.AsyncAnthropic().messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=0.2,
            messages=[{
                "role": "user",
                "content": f"""Analyze this content as a strategic business analyst focused on market implications, 
                growth opportunities, and potential risks.
                Content: {content}"""
            }]
        )
        return response.content

    async def get_jobs_analysis(self, content: str) -> str:
        response = await anthropic.AsyncAnthropic().messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            temperature=0.2,
            messages=[{
                "role": "user",
                "content": f"""Analyze this content as a marketing strategist focused on market positioning, 
                customer value, and go-to-market strategy.
                Content: {content}"""
            }]
        )
        return response.content

    async def get_embedding(self, text: str) -> list:
        response = await anthropic.AsyncAnthropic().embeddings.create(
            model="claude-3-sonnet-20240229",
            input=text
        )
        return response.embeddings[0]