from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    query: str

class TrackInfo(BaseModel):
    artist: str
    song: str
    primary_genre: str
    mood: str
    similarity_score: Optional[float] = None

class ChatResponse(BaseModel):
    response: str
    relevant_tracks: List[TrackInfo]
    insights: List[str] = []

class IngestResponse(BaseModel):
    message: str
    processed_tracks: int
    total_tracks: int

class StatsResponse(BaseModel):
    total_tracks: int
    genres: Dict[str, int]
    moods: Dict[str, int]
    top_artists: List[Dict[str, Any]]
