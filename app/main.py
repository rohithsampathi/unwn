# main.py
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, AsyncGenerator
import asyncio
from datetime import datetime, timezone
import uuid
from newspaper import Article
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import firebase_admin
from firebase_admin import credentials, firestore
import time
from contextlib import asynccontextmanager
import pinecone
import traceback

# Import services
from app.services.classification import MarthaService
from app.services.anthropic import AnthropicService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
required_vars = ["ANTHROPIC_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
if missing := [var for var in required_vars if not os.getenv(var)]:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

# Models
class URLInput(BaseModel):
    urls: List[str] = Field(..., min_items=1, max_items=10)
    analysis_type: str = Field(default="full")
    user_id: Optional[str] = Field(None, min_length=1, max_length=100)

    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        if v not in {'full', 'elon', 'jobs'}:
            raise ValueError('analysis_type must be: full, elon, or jobs')
        return v

class AnalysisInput(BaseModel):
    headline: str
    content: str
    industry: str
    product: str
    elon_analysis: Optional[str]
    jobs_analysis: Optional[str]

class AnalysisResponse(BaseModel):
    title: str
    content: str
    industry: str
    product: str
    elon_analysis: Optional[str]
    jobs_analysis: Optional[str]
    timestamp: int = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()))
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ServiceManager:
    def __init__(self):
        self.pinecone_index = None
        self.firebase_db = None

    async def initialize(self):
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
            )
            self.pinecone_index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))
            
            # Initialize Firebase
            await self._init_firebase()
            return self
        except Exception as e:
            logger.error(f"Service initialization failed: {e}\n{traceback.format_exc()}")
            raise

    async def _init_firebase(self):
        if creds_path := os.getenv("FIREBASE_CREDENTIALS_PATH"):
            if not firebase_admin._apps:
                firebase_admin.initialize_app(credentials.Certificate(creds_path))
            self.firebase_db = firestore.client()

    async def close(self):
        if self.pinecone_index:
            pinecone.deinit()

class MarketAnalyzer:
    def __init__(self, service_manager: ServiceManager):
        self.services = service_manager
        self.martha_service = MarthaService()
        self.anthropic_service = AnthropicService()
        self._last_result = None

    async def analyze_content(self, url: str, analysis_type: str) -> AnalysisResponse:
        try:
            # Extract content
            logger.info(f"Extracting content from: {url}")
            content_data = await self._extract_content(url)
            
            # Get classification
            logger.info("Getting classification")
            classification = await self.martha_service.classify_content(content_data["content"])
            
            # Perform analyses
            analyses = {}
            if analysis_type in {"full", "elon"}:
                logger.info("Performing strategic analysis")
                elon_result = await self.anthropic_service.get_elon_analysis(content_data["content"])
                if elon_result:
                    analyses["elon_analysis"] = elon_result

            if analysis_type in {"full", "jobs"}:
                logger.info("Performing marketing analysis")
                jobs_result = await self.anthropic_service.get_jobs_analysis(content_data["content"])
                if jobs_result:
                    analyses["jobs_analysis"] = jobs_result

            result = AnalysisResponse(
                **content_data,
                **classification,
                **analyses
            )
            
            self._last_result = result.dict()
            logger.info(f"Analysis complete for {url}")
            return result

        except Exception as e:
            logger.error(f"Analysis failed for {url}: {e}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _extract_content(self, url: str) -> Dict[str, str]:
        try:
            article = Article(url)
            await asyncio.to_thread(article.download)
            await asyncio.to_thread(article.parse)
            
            if not article.text:
                raise ValueError("No content extracted from URL")
                
            return {
                "title": article.title or "Untitled",
                "content": article.text
            }
        except Exception as e:
            logger.error(f"Content extraction failed: {e}\n{traceback.format_exc()}")
            raise ValueError(f"Content extraction failed: {str(e)}")

    async def store_analysis(self, data: Dict) -> bool:
        try:
            content_text = f"{data.get('title', '')} {data.get('content', '')}"
            embedding = await self.anthropic_service.get_embedding(content_text)
            
            if not embedding:
                raise ValueError("Failed to generate embedding")

            self.services.pinecone_index.upsert(
                vectors=[(str(uuid.uuid4()), embedding, {
                    "title": data["title"],
                    "industry": data["industry"],
                    "product": data["product"],
                    "elon_analysis": data.get("elon_analysis", ""),
                    "jobs_analysis": data.get("jobs_analysis", ""),
                    "timestamp": data.get("timestamp", int(datetime.now(timezone.utc).timestamp()))
                })]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to store analysis: {e}\n{traceback.format_exc()}")
            return False

# FastAPI Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.service_manager = await ServiceManager().initialize()
        yield
    finally:
        await app.state.service_manager.close()

app = FastAPI(
    title="Market Unwinder",
    description="Market Analysis and Strategy Intelligence Engine",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.post("/analyze-urls", response_model=List[AnalysisResponse])
async def analyze_urls(
    input_data: URLInput,
    service_manager: ServiceManager = Depends(lambda: app.state.service_manager)
):
    analyzer = MarketAnalyzer(service_manager)
    start_time = time.time()
    results = []
    
    for url in input_data.urls:
        try:
            logger.info(f"Processing URL: {url}")
            result = await analyzer.analyze_content(url, input_data.analysis_type)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process URL {url}: {str(e)}")
            continue
    
    logger.info(f"Analysis completed in {time.time() - start_time:.2f}s")
    return results

@app.post("/update-analysis")
async def update_analysis(
    analysis_data: AnalysisInput,
    service_manager: ServiceManager = Depends(lambda: app.state.service_manager)
):
    try:
        analyzer = MarketAnalyzer(service_manager)
        success = await analyzer.store_analysis({
            "title": analysis_data.headline,
            "content": analysis_data.content,
            "industry": analysis_data.industry,
            "product": analysis_data.product,
            "elon_analysis": analysis_data.elon_analysis,
            "jobs_analysis": analysis_data.jobs_analysis
        })
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store analysis")
            
        return {"status": "success", "message": "Analysis stored successfully"}
    except Exception as e:
        logger.error(f"Failed to update analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug-last-analysis")
async def debug_last_analysis(
    service_manager: ServiceManager = Depends(lambda: app.state.service_manager)
):
    try:
        analyzer = MarketAnalyzer(service_manager)
        if hasattr(analyzer, '_last_result'):
            return {"status": "success", "data": analyzer._last_result}
        return {"status": "no_data", "message": "No analysis results found"}
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)