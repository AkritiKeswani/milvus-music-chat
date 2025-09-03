from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import io
import json
from openai import OpenAI
import os

app = FastAPI(title="Music Taste Analyzer", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-loaded music data from your Spotify corpus
music_data = [
    {"artist": "Coldplay", "song": "Yellow", "primary_genre": "pop-rock", "mood": "melancholic"},
    {"artist": "Coldplay", "song": "The Scientist", "primary_genre": "pop-rock", "mood": "melancholic"},
    {"artist": "Coldplay", "song": "Clocks", "primary_genre": "pop-rock", "mood": "upbeat"},
    {"artist": "Coldplay", "song": "Fix You", "primary_genre": "pop-rock", "mood": "melancholic"},
    {"artist": "Coldplay", "song": "Viva La Vida", "primary_genre": "pop-rock", "mood": "upbeat"},
    {"artist": "Coldplay", "song": "Paradise", "primary_genre": "pop-rock", "mood": "upbeat"},
    {"artist": "Coldplay", "song": "A Sky Full of Stars", "primary_genre": "pop-rock", "mood": "upbeat"},
    {"artist": "Coldplay", "song": "Adventure of a Lifetime", "primary_genre": "pop-rock", "mood": "upbeat"},
    {"artist": "OneRepublic", "song": "Apologize", "primary_genre": "pop-rock", "mood": "melancholic"},
    {"artist": "OneRepublic", "song": "Stop And Stare", "primary_genre": "pop-rock", "mood": "chill"},
    {"artist": "OneRepublic", "song": "All The Right Moves", "primary_genre": "pop-rock", "mood": "energetic"},
    {"artist": "OneRepublic", "song": "Secrets", "primary_genre": "pop-rock", "mood": "melancholic"},
    {"artist": "OneRepublic", "song": "Good Life", "primary_genre": "pop-rock", "mood": "upbeat"},
    {"artist": "OneRepublic", "song": "Counting Stars", "primary_genre": "pop-rock", "mood": "upbeat"},
    {"artist": "OneRepublic", "song": "Feel Again", "primary_genre": "pop-rock", "mood": "chill"},
    {"artist": "OneRepublic", "song": "I Lived", "primary_genre": "pop-rock", "mood": "upbeat"},
    {"artist": "OneRepublic", "song": "Somebody To Love", "primary_genre": "pop-rock", "mood": "romantic"},
    {"artist": "Luke Combs", "song": "Beautiful Crazy", "primary_genre": "country", "mood": "romantic"},
    {"artist": "Chris Stapleton", "song": "Tennessee Whiskey", "primary_genre": "country", "mood": "romantic"},
    {"artist": "Chris Stapleton", "song": "You Should Probably Leave", "primary_genre": "country", "mood": "melancholic"},
    {"artist": "Mr. Probz", "song": "Space For Two", "primary_genre": "alternative", "mood": "chill"},
    {"artist": "Dan + Shay", "song": "Speechless", "primary_genre": "country", "mood": "romantic"},
    {"artist": "Dan + Shay", "song": "Tequila", "primary_genre": "country", "mood": "nostalgic"},
    {"artist": "Morgan Wallen", "song": "Last Night", "primary_genre": "country", "mood": "nostalgic"},
    {"artist": "Morgan Wallen", "song": "Just In Case", "primary_genre": "country", "mood": "nostalgic"},
    {"artist": "Morgan Wallen", "song": "More Than My Hometown", "primary_genre": "country", "mood": "nostalgic"},
    {"artist": "Morgan Wallen", "song": "7 Summers", "primary_genre": "country", "mood": "nostalgic"},
    {"artist": "Cody Johnson", "song": "I'm Gonna Love You", "primary_genre": "country", "mood": "romantic"},
    {"artist": "Colbie Caillat", "song": "Realize", "primary_genre": "indie-folk", "mood": "chill"},
    {"artist": "Dylan Gossett", "song": "Coal", "primary_genre": "country", "mood": "nostalgic"},
    {"artist": "Brett Young", "song": "In Case You Didn't Know", "primary_genre": "country", "mood": "romantic"},
    {"artist": "Florida Georgia Line", "song": "Dirt", "primary_genre": "country", "mood": "nostalgic"},
    {"artist": "Jason Mraz", "song": "Lucky", "primary_genre": "indie-folk", "mood": "romantic"},
    {"artist": "Howie Day", "song": "Collide", "primary_genre": "indie-folk", "mood": "melancholic"},
    {"artist": "Noor Chahal", "song": "Janiye", "primary_genre": "bollywood", "mood": "romantic"},
    {"artist": "Noor Chahal", "song": "Rooh", "primary_genre": "bollywood", "mood": "melancholic"},
    {"artist": "ABRA", "song": "Gimme! Gimme! Gimme!", "primary_genre": "electronic", "mood": "energetic"},
    {"artist": "Kygo", "song": "Stole the Show", "primary_genre": "electronic", "mood": "upbeat"},
    {"artist": "Kygo", "song": "For Life", "primary_genre": "electronic", "mood": "upbeat"},
    {"artist": "Kygo", "song": "Whatever", "primary_genre": "electronic", "mood": "chill"},
    {"artist": "Kygo", "song": "It Ain't Me", "primary_genre": "electronic", "mood": "chill"},
    {"artist": "Rahul Vaidya", "song": "Madhanya", "primary_genre": "bollywood", "mood": "romantic"},
    {"artist": "Sade", "song": "By Your Side", "primary_genre": "alternative", "mood": "romantic"},
    {"artist": "Declan McKenna", "song": "Brazil", "primary_genre": "indie-folk", "mood": "energetic"},
    {"artist": "Geowulf", "song": "Saltwater", "primary_genre": "indie-folk", "mood": "chill"},
    {"artist": "HARBOUR", "song": "Float", "primary_genre": "indie-folk", "mood": "chill"},
    {"artist": "Del Water Gap", "song": "All We Ever Do Is Talk", "primary_genre": "indie-folk", "mood": "melancholic"},
    {"artist": "Megan Davies", "song": "Infinite", "primary_genre": "indie-folk", "mood": "chill"},
    {"artist": "Death Cab for Cutie", "song": "Do You Remember", "primary_genre": "indie-folk", "mood": "nostalgic"},
    {"artist": "Death Cab for Cutie", "song": "Your New Twin Sized Bed", "primary_genre": "indie-folk", "mood": "melancholic"},
    {"artist": "Marcy Playground", "song": "Sex & Candy", "primary_genre": "alternative", "mood": "chill"},
    {"artist": "AUR", "song": "Shikayat", "primary_genre": "bollywood", "mood": "melancholic"},
    {"artist": "Rey Woods", "song": "Drama", "primary_genre": "alternative", "mood": "energetic"},
    {"artist": "CAPT", "song": "Gehraiyaan Title Track", "primary_genre": "bollywood", "mood": "melancholic"},
    {"artist": "Arijit Singh", "song": "California's Burning", "primary_genre": "bollywood", "mood": "melancholic"},
    {"artist": "Arooj Aftab", "song": "Mohabbat", "primary_genre": "bollywood", "mood": "romantic"},
    {"artist": "Ty Myers", "song": "Thought It Was Love", "primary_genre": "alternative", "mood": "melancholic"},
    {"artist": "Xnoob", "song": "Far Away Place - Rampa Remix", "primary_genre": "electronic", "mood": "chill"},
    {"artist": "Baji", "song": "tell you straight", "primary_genre": "alternative", "mood": "chill"},
    {"artist": "Drake", "song": "No Face", "primary_genre": "alternative", "mood": "chill"},
    {"artist": "Scultaneous Bohemian", "song": "One By One", "primary_genre": "alternative", "mood": "chill"},
    {"artist": "JAY-Z", "song": "Real As It Gets", "primary_genre": "alternative", "mood": "energetic"},
    {"artist": "Antonio Williams", "song": "Changes", "primary_genre": "alternative", "mood": "melancholic"},
    {"artist": "Big Red Machine", "song": "Thoughts in Progress", "primary_genre": "indie-folk", "mood": "melancholic"},
    {"artist": "The Japanese House", "song": "Dionne", "primary_genre": "indie-folk", "mood": "chill"},
    {"artist": "Big Red Machine", "song": "June's a River", "primary_genre": "indie-folk", "mood": "nostalgic"},
    {"artist": "Big Red Machine", "song": "Phoenix", "primary_genre": "indie-folk", "mood": "melancholic"}
]

class ChatRequest(BaseModel):
    query: str

class TrackInfo(BaseModel):
    artist: str
    song: str
    primary_genre: str
    mood: str

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

def analyze_track_simple(artist: str, song: str) -> Dict[str, str]:
    """Simple rule-based analysis for your specific corpus"""
    artist_lower = artist.lower()
    song_lower = song.lower()
    
    # Genre mapping based on your corpus
    if artist_lower in ['coldplay', 'onerepublic']:
        genre = 'pop-rock'
    elif artist_lower in ['morgan wallen', 'luke combs', 'chris stapleton', 'dan + shay', 'cody johnson', 'brett young', 'florida georgia line', 'dylan gossett']:
        genre = 'country'
    elif artist_lower in ['kygo']:
        genre = 'electronic'
    elif artist_lower in ['noor chahal', 'rahul vaidya', 'arijit singh', 'aur', 'capt']:
        genre = 'bollywood'
    elif artist_lower in ['death cab for cutie', 'big red machine', 'the japanese house', 'declan mckenna', 'geowulf', 'harbour', 'del water gap']:
        genre = 'indie-folk'
    else:
        genre = 'alternative'
    
    # Mood mapping based on song characteristics
    melancholic_words = ['scientist', 'fix you', 'yellow', 'apologize', 'secrets', 'beautiful crazy', 'tennessee whiskey', 'speechless', 'realize', 'collide', 'by your side']
    upbeat_words = ['clocks', 'viva la vida', 'paradise', 'sky full of stars', 'adventure', 'counting stars', 'good life', 'stole the show', 'for life', 'whatever']
    nostalgic_words = ['last night', '7 summers', 'more than my hometown', 'coal', 'dirt', 'lucky']
    romantic_words = ['speechless', 'tequila', 'in case you didn\'t know', 'lucky', 'by your side']
    
    if any(word in song_lower for word in melancholic_words):
        mood = 'melancholic'
    elif any(word in song_lower for word in upbeat_words):
        mood = 'upbeat'
    elif any(word in song_lower for word in nostalgic_words):
        mood = 'nostalgic'
    elif any(word in song_lower for word in romantic_words):
        mood = 'romantic'
    elif genre == 'electronic':
        mood = 'energetic'
    else:
        mood = 'chill'
    
    return {"primary_genre": genre, "mood": mood}

@app.get("/")
async def root():
    return {"message": "Music Taste Analyzer API - Simple Version"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_music(file: UploadFile = File(...)):
    """Upload and process music library CSV file"""
    global music_data
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        if 'artist' not in df.columns or 'song' not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'artist' and 'song' columns")
        
        music_data = []
        for _, row in df.iterrows():
            artist = row['artist']
            song = row['song']
            analysis = analyze_track_simple(artist, song)
            
            music_data.append({
                "artist": artist,
                "song": song,
                "primary_genre": analysis["primary_genre"],
                "mood": analysis["mood"]
            })
        
        return IngestResponse(
            message="Music library processed successfully",
            processed_tracks=len(music_data),
            total_tracks=len(df)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """Process natural language queries about music taste"""
    if not music_data:
        raise HTTPException(status_code=400, detail="No music library uploaded yet")
    
    query_lower = request.query.lower()
    relevant_tracks = []
    
    # Simple keyword matching for your corpus
    if 'country' in query_lower:
        relevant_tracks = [track for track in music_data if track['primary_genre'] == 'country'][:5]
    elif 'pop' in query_lower or 'rock' in query_lower:
        relevant_tracks = [track for track in music_data if track['primary_genre'] == 'pop-rock'][:5]
    elif 'electronic' in query_lower:
        relevant_tracks = [track for track in music_data if track['primary_genre'] == 'electronic'][:5]
    elif 'sad' in query_lower or 'melancholic' in query_lower:
        relevant_tracks = [track for track in music_data if track['mood'] == 'melancholic'][:5]
    elif 'happy' in query_lower or 'upbeat' in query_lower:
        relevant_tracks = [track for track in music_data if track['mood'] == 'upbeat'][:5]
    elif 'chill' in query_lower:
        relevant_tracks = [track for track in music_data if track['mood'] == 'chill'][:5]
    else:
        # Default to showing some variety
        genres = list(set([track['primary_genre'] for track in music_data]))
        relevant_tracks = []
        for genre in genres[:3]:
            genre_tracks = [track for track in music_data if track['primary_genre'] == genre]
            if genre_tracks:
                relevant_tracks.append(genre_tracks[0])
    
    # Generate response
    if relevant_tracks:
        genres = list(set([track['primary_genre'] for track in relevant_tracks]))
        moods = list(set([track['mood'] for track in relevant_tracks]))
        
        response = f"Based on your music library, I found {len(relevant_tracks)} relevant tracks. "
        response += f"Your music spans {', '.join(genres)} genres with {', '.join(moods)} moods. "
        
        if 'country' in query_lower:
            response += "You have a strong country music preference with artists like Morgan Wallen and Chris Stapleton."
        elif 'pop' in query_lower:
            response += "Your pop-rock taste includes mainstream favorites like Coldplay and OneRepublic."
        else:
            response += f"Your top track is {relevant_tracks[0]['artist']} - {relevant_tracks[0]['song']}."
    else:
        response = "I couldn't find specific matches for your query, but your music library shows diverse taste across multiple genres."
    
    track_objects = [TrackInfo(**track) for track in relevant_tracks]
    
    return ChatResponse(
        response=response,
        relevant_tracks=track_objects,
        insights=[f"You have {len(music_data)} total tracks", f"Most common genre: {max(set([t['primary_genre'] for t in music_data]), key=[t['primary_genre'] for t in music_data].count)}"]
    )

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about the music library"""
    if not music_data:
        raise HTTPException(status_code=400, detail="No music library uploaded yet")
    
    # Calculate stats
    genres = {}
    moods = {}
    artists = {}
    
    for track in music_data:
        genres[track['primary_genre']] = genres.get(track['primary_genre'], 0) + 1
        moods[track['mood']] = moods.get(track['mood'], 0) + 1
        artists[track['artist']] = artists.get(track['artist'], 0) + 1
    
    top_artists = [{"artist": artist, "count": count} for artist, count in sorted(artists.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    return StatsResponse(
        total_tracks=len(music_data),
        genres=genres,
        moods=moods,
        top_artists=top_artists
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
