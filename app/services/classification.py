# app/services/classification.py

import anthropic
from app.core.config import settings
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class MarthaService:
    def __init__(self):
        self.client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)

    async def classify_content(self, content: str) -> Dict:
        try:
            response = await anthropic.AsyncAnthropic().messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                temperature=0.5,
                messages=[{
                    "role": "user",
                    "content": """You are Martha, an expert content classifier. Your task is to classify the given content into industry and product category based on the context.
                     The valid industry categories are:
                     - Food Tech
                     - Health Tech
                     - Semiconductors
                     - EV
                     - Transportation
                     - Agri Tech
                     - Animal Feed & Pet Care
                     - AI
                     - Aerospace
                     - Insurance & Financial Services
                     Classify the following content:
                     <content>
                    {content}
                     </content>
                     Think through your classification:
                     1. Key terms and concepts in the content
                     2. Most relevant industry from the list
                     3. Specific product or service mentioned
                     Provide ONLY your final classification in this exact format:
                     Industry: [industry]
                     Product: [product]""".format(content=content)
                }]
            )

            # Extract text from response
            if isinstance(response.content, list):
                result_text = response.content[0].text
            else:
                result_text = str(response.content)

            # Log raw response for debugging
            logger.debug(f"Raw classification response: {result_text}")

            # Parse response
            lines = [line.strip() for line in result_text.split('\n') if line.strip()]
            
            industry = "Unknown"
            product = "Unknown"

            for line in lines:
                if ':' in line:
                    key, value = [x.strip() for x in line.split(':', 1)]
                    if key.lower() == 'industry':
                        industry = value
                    elif key.lower() == 'product':
                        product = value

            logger.info(f"Final classification - Industry: {industry}, Product: {product}")
            return {"industry": industry, "product": product}

        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return {"industry": "Classification failed", "product": "Classification failed"}