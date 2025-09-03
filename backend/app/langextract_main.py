from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import langextract as lx
import textwrap
from google import genai
from google.genai.types import EmbedContentConfig
from pymilvus import MilvusClient, DataType
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Music Taste Analyzer - LangExtract + Milvus", version="2.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
genai_client = genai.Client()
COLLECTION_NAME = "music_extractions"
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 3072

# Initialize Milvus client
milvus_client = MilvusClient(uri="./milvus_music.db")

# Your Spotify corpus
SPOTIFY_CORPUS = [
    {"artist": "Coldplay", "song": "Yellow"},
    {"artist": "Coldplay", "song": "The Scientist"},
    {"artist": "Coldplay", "song": "Clocks"},
    {"artist": "Coldplay", "song": "Fix You"},
    {"artist": "Coldplay", "song": "Viva La Vida"},
    {"artist": "Coldplay", "song": "Paradise"},
    {"artist": "Coldplay", "song": "A Sky Full of Stars"},
    {"artist": "Coldplay", "song": "Adventure of a Lifetime"},
    {"artist": "OneRepublic", "song": "Apologize"},
    {"artist": "OneRepublic", "song": "Stop And Stare"},
    {"artist": "OneRepublic", "song": "All The Right Moves"},
    {"artist": "OneRepublic", "song": "Secrets"},
    {"artist": "OneRepublic", "song": "Good Life"},
    {"artist": "OneRepublic", "song": "Counting Stars"},
    {"artist": "OneRepublic", "song": "Feel Again"},
    {"artist": "OneRepublic", "song": "I Lived"},
    {"artist": "OneRepublic", "song": "Somebody To Love"},
    {"artist": "Luke Combs", "song": "Beautiful Crazy"},
    {"artist": "Chris Stapleton", "song": "Tennessee Whiskey"},
    {"artist": "Chris Stapleton", "song": "You Should Probably Leave"},
    {"artist": "Mr. Probz", "song": "Space For Two"},
    {"artist": "Dan + Shay", "song": "Speechless"},
    {"artist": "Dan + Shay", "song": "Tequila"},
    {"artist": "Morgan Wallen", "song": "Last Night"},
    {"artist": "Morgan Wallen", "song": "Just In Case"},
    {"artist": "Morgan Wallen", "song": "More Than My Hometown"},
    {"artist": "Morgan Wallen", "song": "7 Summers"},
    {"artist": "Cody Johnson", "song": "I'm Gonna Love You"},
    {"artist": "Colbie Caillat", "song": "Realize"},
    {"artist": "Dylan Gossett", "song": "Coal"},
    {"artist": "Brett Young", "song": "In Case You Didn't Know"},
    {"artist": "Florida Georgia Line", "song": "Dirt"},
    {"artist": "Jason Mraz", "song": "Lucky"},
    {"artist": "Howie Day", "song": "Collide"},
    {"artist": "Noor Chahal", "song": "Janiye"},
    {"artist": "Noor Chahal", "song": "Rooh"},
    {"artist": "ABRA", "song": "Gimme! Gimme! Gimme!"},
    {"artist": "Kygo", "song": "Stole the Show"},
    {"artist": "Kygo", "song": "For Life"},
    {"artist": "Kygo", "song": "Whatever"},
    {"artist": "Kygo", "song": "It Ain't Me"},
    {"artist": "Rahul Vaidya", "song": "Madhanya"},
    {"artist": "Sade", "song": "By Your Side"},
    {"artist": "Declan McKenna", "song": "Brazil"},
    {"artist": "Geowulf", "song": "Saltwater"},
    {"artist": "HARBOUR", "song": "Float"},
    {"artist": "Del Water Gap", "song": "All We Ever Do Is Talk"},
    {"artist": "Megan Davies", "song": "Infinite"},
    {"artist": "Death Cab for Cutie", "song": "Do You Remember"},
    {"artist": "Death Cab for Cutie", "song": "Your New Twin Sized Bed"},
    {"artist": "Marcy Playground", "song": "Sex & Candy"},
    {"artist": "AUR", "song": "Shikayat"},
    {"artist": "Rey Woods", "song": "Drama"},
    {"artist": "CAPT", "song": "Gehraiyaan Title Track"},
    {"artist": "Arijit Singh", "song": "California's Burning"},
    {"artist": "Arooj Aftab", "song": "Mohabbat"},
    {"artist": "Ty Myers", "song": "Thought It Was Love"},
    {"artist": "Xnoob", "song": "Far Away Place - Rampa Remix"},
    {"artist": "Baji", "song": "tell you straight"},
    {"artist": "Drake", "song": "No Face"},
    {"artist": "Scultaneous Bohemian", "song": "One By One"},
    {"artist": "JAY-Z", "song": "Real As It Gets"},
    {"artist": "Antonio Williams", "song": "Changes"},
    {"artist": "Big Red Machine", "song": "Thoughts in Progress"},
    {"artist": "The Japanese House", "song": "Dionne"},
    {"artist": "Big Red Machine", "song": "June's a River"},
    {"artist": "Big Red Machine", "song": "Phoenix"}
]

class ChatRequest(BaseModel):
    query: str

class TrackInfo(BaseModel):
    artist: str
    song: str
    primary_genre: str
    mood: str
    similarity_score: float = 0.0

class ChatResponse(BaseModel):
    response: str
    relevant_tracks: List[TrackInfo]
    insights: List[str] = []

def setup_milvus_collection():
    """Set up Milvus collection with proper schema"""
    # Drop existing collection if it exists
    if milvus_client.has_collection(collection_name=COLLECTION_NAME):
        milvus_client.drop_collection(collection_name=COLLECTION_NAME)
    
    # Create collection schema
    schema = milvus_client.create_schema(
        auto_id=False,
        enable_dynamic_field=True,
        description="Music track extraction results and vector storage",
    )
    
    # Add fields
    schema.add_field(
        field_name="id", datatype=DataType.VARCHAR, max_length=100, is_primary=True
    )
    schema.add_field(
        field_name="track_info", datatype=DataType.VARCHAR, max_length=1000
    )
    schema.add_field(
        field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM
    )
    schema.add_field(
        field_name="artist", datatype=DataType.VARCHAR, max_length=200
    )
    schema.add_field(
        field_name="song", datatype=DataType.VARCHAR, max_length=200
    )
    
    # Create collection
    milvus_client.create_collection(collection_name=COLLECTION_NAME, schema=schema)
    
    # Create vector index
    index_params = milvus_client.prepare_index_params()
    index_params.add_index(
        field_name="embedding",
        index_type="AUTOINDEX",
        metric_type="COSINE",
    )
    milvus_client.create_index(collection_name=COLLECTION_NAME, index_params=index_params)

def get_langextract_examples():
    """Define examples for LangExtract to guide music analysis"""
    return [
        lx.data.ExampleData(
            text="Artist: Coldplay, Song: Yellow",
            extractions=[
                lx.data.Extraction(
                    extraction_class="music_analysis",
                    extraction_text="Coldplay - Yellow",
                    attributes={"primary_genre": "pop-rock", "mood": "melancholic"},
                )
            ],
        ),
        lx.data.ExampleData(
            text="Artist: Morgan Wallen, Song: Last Night",
            extractions=[
                lx.data.Extraction(
                    extraction_class="music_analysis",
                    extraction_text="Morgan Wallen - Last Night",
                    attributes={"primary_genre": "country", "mood": "nostalgic"},
                )
            ],
        ),
        lx.data.ExampleData(
            text="Artist: Kygo, Song: Stole the Show",
            extractions=[
                lx.data.Extraction(
                    extraction_class="music_analysis",
                    extraction_text="Kygo - Stole the Show",
                    attributes={"primary_genre": "electronic", "mood": "upbeat"},
                )
            ],
        ),
    ]

def get_langextract_prompt():
    """Define the extraction prompt for music analysis"""
    return textwrap.dedent("""
    Analyze music tracks and extract the primary genre and mood from "Artist: X, Song: Y" format.
    Focus on the most representative genre and dominant emotional tone based on the artist's style and song characteristics.
    
    Use these exact attribute values based on the user's personal music taste:
    
    primary_genre: ["pop-rock", "indie-folk", "country", "electronic", "alternative", "bollywood"]
    mood: ["melancholic", "upbeat", "chill", "nostalgic", "romantic", "energetic"]
    
    Consider the artist's typical style and the song's characteristics. This is a personal music library
    with mainstream pop-rock (Coldplay, OneRepublic), country (Morgan Wallen, Chris Stapleton), 
    electronic (Kygo), and some international tracks.
    """)

def process_music_corpus():
    """Process the Spotify corpus using LangExtract and store in Milvus"""
    print("Processing music corpus with LangExtract...")
    
    examples = get_langextract_examples()
    prompt = get_langextract_prompt()
    processed_data = []
    
    for track in SPOTIFY_CORPUS:
        artist = track["artist"]
        song = track["song"]
        track_text = f"Artist: {artist}, Song: {song}"
        
        try:
            # Extract using LangExtract
            result = lx.extract(
                text_or_documents=track_text,
                prompt_description=prompt,
                examples=examples,
                model_id="gemini-2.0-flash",
            )
            
            # Generate embedding
            embedding_response = genai_client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=[track_text],
                config=EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=EMBEDDING_DIM,
                ),
            )
            embedding = embedding_response.embeddings[0].values
            
            # Process extraction results
            primary_genre = "alternative"  # default
            mood = "chill"  # default
            
            for extraction in result.extractions:
                if extraction.extraction_class == "music_analysis":
                    attrs = extraction.attributes or {}
                    primary_genre = attrs.get("primary_genre", "alternative")
                    mood = attrs.get("mood", "chill")
                    break
            
            # Prepare data entry
            data_entry = {
                "id": f"track_{uuid.uuid4().hex[:8]}",
                "track_info": track_text,
                "embedding": embedding,
                "artist": artist,
                "song": song,
                "primary_genre": primary_genre,
                "mood": mood,
            }
            
            processed_data.append(data_entry)
            print(f"Processed: {artist} - {song} -> {primary_genre}, {mood}")
            
        except Exception as e:
            print(f"Error processing {artist} - {song}: {e}")
            continue
    
    # Insert into Milvus
    if processed_data:
        milvus_client.insert(collection_name=COLLECTION_NAME, data=processed_data)
        milvus_client.load_collection(collection_name=COLLECTION_NAME)
        print(f"Successfully processed and stored {len(processed_data)} tracks")
    
    return len(processed_data)

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    setup_milvus_collection()
    process_music_corpus()

@app.get("/")
async def root():
    return {"message": "Music Taste Analyzer - LangExtract + Milvus Integration"}

@app.post("/chat", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """Process natural language queries using semantic search"""
    try:
        # Generate query embedding
        query_embedding_response = genai_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=[request.query],
            config=EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=EMBEDDING_DIM,
            ),
        )
        query_embedding = query_embedding_response.embeddings[0].values
        
        # Semantic search in Milvus
        search_results = milvus_client.search(
            collection_name=COLLECTION_NAME,
            data=[query_embedding],
            anns_field="embedding",
            limit=5,
            output_fields=["track_info", "artist", "song", "primary_genre", "mood"],
            search_params={"metric_type": "COSINE"},
        )
        
        relevant_tracks = []
        if search_results and search_results[0]:
            for result in search_results[0]:
                similarity_score = 1 - result["distance"]  # Convert distance to similarity
                relevant_tracks.append(TrackInfo(
                    artist=result.get("artist", "Unknown"),
                    song=result.get("song", "Unknown"),
                    primary_genre=result.get("primary_genre", "unknown"),
                    mood=result.get("mood", "unknown"),
                    similarity_score=similarity_score
                ))
        
        # Generate intelligent response
        response = await generate_response(request.query, relevant_tracks)
        insights = generate_insights(relevant_tracks)
        
        return ChatResponse(
            response=response,
            relevant_tracks=relevant_tracks,
            insights=insights
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

async def generate_response(query: str, tracks: List[TrackInfo]) -> str:
    """Generate an intelligent response based on the query and retrieved tracks"""
    if not tracks:
        return "I don't have any matching tracks for that query. Try asking about genres like pop-rock, country, electronic, or moods like melancholic, upbeat, or nostalgic."
    
    query_lower = query.lower()
    
    # Analyze the retrieved tracks
    genres = [track.primary_genre for track in tracks]
    moods = [track.mood for track in tracks]
    artists = [track.artist for track in tracks]
    
    from collections import Counter
    genre_counts = Counter(genres)
    mood_counts = Counter(moods)
    
    # Generate contextual response
    if any(word in query_lower for word in ['recommend', 'suggest', 'should listen']):
        response = f"Based on your music taste, I'd recommend these tracks:\n\n"
        for i, track in enumerate(tracks[:3], 1):
            response += f"{i}. **{track.artist} - {track.song}** ({track.primary_genre}, {track.mood})\n"
        response += f"\nThese match your query with {tracks[0].similarity_score:.1%} similarity!"
    
    elif any(word in query_lower for word in ['genre', 'style', 'type']):
        dominant_genre = genre_counts.most_common(1)[0][0]
        response = f"Your music taste leans heavily toward **{dominant_genre}**. "
        response += f"Looking at your top matches, you have {genre_counts[dominant_genre]} {dominant_genre} tracks including "
        response += f"**{tracks[0].artist} - {tracks[0].song}** and **{tracks[1].artist} - {tracks[1].song}**."
    
    elif any(word in query_lower for word in ['mood', 'feel', 'emotion', 'vibe']):
        dominant_mood = mood_counts.most_common(1)[0][0]
        response = f"Your music has a predominantly **{dominant_mood}** vibe. "
        response += f"Songs like **{tracks[0].artist} - {tracks[0].song}** capture this {dominant_mood} feeling perfectly."
    
    elif any(word in query_lower for word in ['sad', 'melancholic', 'emotional']):
        sad_tracks = [t for t in tracks if t.mood in ['melancholic', 'nostalgic']]
        if sad_tracks:
            response = f"When you're feeling emotional, you turn to tracks like **{sad_tracks[0].artist} - {sad_tracks[0].song}**. "
            response += f"Your {sad_tracks[0].mood} music taste includes beautiful songs that resonate with deeper emotions."
        else:
            response = "Your music library has some emotional depth, though the current matches lean more toward upbeat vibes."
    
    else:
        # General response
        response = f"Based on your music taste, here are your top matches:\n\n"
        for track in tracks[:3]:
            response += f"• **{track.artist} - {track.song}** ({track.primary_genre}, {track.mood})\n"
        response += f"\nYour music spans {len(set(genres))} genres with a preference for {genre_counts.most_common(1)[0][0]} music."
    
    return response

def generate_insights(tracks: List[TrackInfo]) -> List[str]:
    """Generate insights about the retrieved tracks"""
    if not tracks:
        return []
    
    insights = []
    
    from collections import Counter
    genres = Counter([track.primary_genre for track in tracks])
    moods = Counter([track.mood for track in tracks])
    
    # Genre insights
    if len(genres) > 1:
        insights.append(f"Your taste spans {len(genres)} genres: {', '.join(genres.keys())}")
    else:
        insights.append(f"Strong preference for {list(genres.keys())[0]} music")
    
    # Mood insights
    dominant_mood = moods.most_common(1)[0][0]
    insights.append(f"Dominant mood: {dominant_mood}")
    
    # Similarity insights
    avg_similarity = sum(track.similarity_score for track in tracks) / len(tracks)
    insights.append(f"Average match: {avg_similarity:.1%}")
    
    return insights

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
