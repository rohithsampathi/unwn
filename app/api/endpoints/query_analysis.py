# app/api/endpoints/query_analysis.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryInput
from app.services.anthropic import AnthropicService
from app.services.pinecone import PineconeService
from app.services.firebase import FirebaseService
import logging

router = APIRouter()
anthropic_service = AnthropicService()
pinecone_service = PineconeService()
firebase_service = FirebaseService()

@router.post("/analyze-query")
async def analyze_query(input_data: QueryInput):
    try:
        # Get similar content from Pinecone
        similar_results = await pinecone_service.search_similar(input_data.query)
        
        # Prepare context from search results
        context = "\n\n".join([
            match.metadata.get("elon_analysis", "")
            for match in similar_results
            if match.metadata.get("elon_analysis")
        ])
        
        # Get analysis based on engine type
        if input_data.engine == "swot":
            prompt = f"""Perform a SWOT analysis for {input_data.query} considering:
            Context: {context}"""
        elif input_data.engine == "porters":
            prompt = f"""Perform a Porter's Five Forces analysis for {input_data.query} considering:
            Context: {context}"""
        else:
            prompt = f"""Analyze {input_data.query} using {input_data.engine} framework considering:
            Context: {context}"""
        
        # Get analysis
        analysis_result = await anthropic_service.get_elon_analysis(prompt)
        
        # Store conversation
        await firebase_service.store_conversation(
            input_data.user_id,
            input_data.conversation_id,
            {
                "query": input_data.query,
                "engine": input_data.engine,
                "result": analysis_result,
                "mind": input_data.mind
            }
        )
        
        return {"result": analysis_result}
        
    except Exception as e:
        logging.error(f"Error analyzing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    try:
        conversations = await firebase_service.get_conversations(user_id)
        return conversations or {"conversations": {}}
    except Exception as e:
        logging.error(f"Error retrieving conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))