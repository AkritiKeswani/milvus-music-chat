from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

from .services.music_analyzer import MusicAnalyzer
from .models.schemas import ChatRequest, ChatResponse, IngestResponse, StatsResponse

# Load environment variables
load_dotenv()

app = FastAPI(title="Music Taste Analyzer", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize music analyzer
music_analyzer = MusicAnalyzer()

@app.on_event("startup")
async def startup_event():
    """Initialize Milvus connection on startup"""
    await music_analyzer.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    await music_analyzer.cleanup()

@app.get("/")
async def root():
    return {"message": "Music Taste Analyzer API"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_music(file: UploadFile = File(...)):
    """
    Upload and process music library CSV file.
    Expected format: artist,song
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        content = await file.read()
        result = await music_analyzer.ingest_csv(content)
        return IngestResponse(
            message="Music library processed successfully",
            processed_tracks=result["processed_tracks"],
            total_tracks=result["total_tracks"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Process natural language queries about music taste
    """
    try:
        result = await music_analyzer.query_music_taste(request.query)
        return ChatResponse(
            response=result["response"],
            relevant_tracks=result["relevant_tracks"],
            insights=result.get("insights", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get statistics about the music library
    """
    try:
        stats = await music_analyzer.get_library_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
