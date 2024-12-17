# app/services/pinecone.py
import pinecone
from app.core.config import settings
from typing import Dict, List
import uuid
import logging
from .anthropic import AnthropicService

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
        self.anthropic_service = AnthropicService()

    async def store_analysis(self, data: Dict) -> bool:
        try:
            # Create embedding for the content
            content_text = f"{data.get('title', '')} {data.get('content', '')}"
            vector = await self.anthropic_service.get_embedding(content_text)
            
            # Format metadata
            metadata = {
                "title": data.get("title", ""),
                "industry": data.get("industry", ""),
                "product": data.get("product", ""),
                "elon_analysis": data.get("elon_analysis", ""),
                "jobs_analysis": data.get("jobs_analysis", ""),
                "timestamp": data.get("timestamp", ""),
                "url": data.get("url", "")
            }
            
            # Remove None values from metadata
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            # Generate unique ID
            vector_id = str(uuid.uuid4())
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(vector_id, vector, metadata)]
            )
            
            logger.info(f"Successfully stored analysis with ID: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing in Pinecone: {e}")
            return False

    async def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        try:
            # Get embedding for query
            vector = await self.anthropic_service.get_embedding(query)
            
            # Search Pinecone
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True
            )
            
            return results.matches
            
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []

    async def delete_vector(self, vector_id: str) -> bool:
        try:
            self.index.delete(ids=[vector_id])
            logger.info(f"Successfully deleted vector: {vector_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting vector: {e}")
            return False

    async def update_metadata(self, vector_id: str, metadata: Dict) -> bool:
        try:
            # Get existing vector
            vector_data = self.index.fetch([vector_id])
            if not vector_data.vectors:
                raise ValueError(f"Vector {vector_id} not found")
                
            # Update with new metadata
            existing_vector = vector_data.vectors[vector_id]
            updated_metadata = {**existing_vector.metadata, **metadata}
            
            # Upsert updated vector
            self.index.upsert(
                vectors=[(vector_id, existing_vector.values, updated_metadata)]
            )
            
            logger.info(f"Successfully updated metadata for vector: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            return False