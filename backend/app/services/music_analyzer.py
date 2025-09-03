import langextract as lx
import pandas as pd
import io
import uuid
from typing import List, Dict, Any
from collections import Counter
from google import genai
from google.genai.types import EmbedContentConfig
from pymilvus import MilvusClient, DataType
import os

class MusicAnalyzer:
    def __init__(self):
        self.genai_client = genai.Client()
        self.collection_name = "music_extractions"
        self.embedding_model = "gemini-embedding-001"
        self.embedding_dim = 3072
        self.client = None
        
        # Ensure GEMINI_API_KEY is set
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    async def initialize(self):
        """Initialize Milvus connection and create collection if needed"""
        self.client = MilvusClient(uri="./milvus_music.db")
        await self._setup_collection()
    
    async def cleanup(self):
        """Clean up resources"""
        if self.client:
            self.client.close()
    
    async def _setup_collection(self):
        """Set up Milvus collection with proper schema"""
        # Drop existing collection if it exists
        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)
        
        # Create collection schema
        schema = self.client.create_schema(
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
            field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=self.embedding_dim
        )
        schema.add_field(
            field_name="artist", datatype=DataType.VARCHAR, max_length=200
        )
        schema.add_field(
            field_name="song", datatype=DataType.VARCHAR, max_length=200
        )
        
        # Create collection
        self.client.create_collection(collection_name=self.collection_name, schema=schema)
        
        # Create vector index
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )
        self.client.create_index(collection_name=self.collection_name, index_params=index_params)
    
    def _get_extraction_examples(self):
        """Define examples for LangExtract to guide music genre and mood extraction"""
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
    
    def _get_extraction_prompt(self):
        """Define the extraction prompt for music analysis"""
        return """
        Analyze music tracks and extract the primary genre and mood from "Artist: X, Song: Y" format.
        Focus on the most representative genre and dominant emotional tone.
        
        Use these exact attribute values based on the user's music taste:
        
        primary_genre: ["pop-rock", "indie-folk", "country", "electronic", "alternative", "bollywood"]
        mood: ["melancholic", "upbeat", "chill", "nostalgic", "romantic", "energetic"]
        
        Consider the artist's typical style and the song's characteristics. This is a personal music library
        with mainstream pop-rock (Coldplay, OneRepublic), country (Morgan Wallen, Chris Stapleton), 
        electronic (Kygo), and some international tracks.
        """
    
    async def ingest_csv(self, csv_content: bytes) -> Dict[str, Any]:
        """Process CSV file and extract music data using LangExtract"""
        # Parse CSV
        df = pd.read_csv(io.StringIO(csv_content.decode('utf-8')))
        
        if 'artist' not in df.columns or 'song' not in df.columns:
            raise ValueError("CSV must contain 'artist' and 'song' columns")
        
        processed_data = []
        examples = self._get_extraction_examples()
        prompt = self._get_extraction_prompt()
        
        for _, row in df.iterrows():
            artist = row['artist']
            song = row['song']
            track_text = f"Artist: {artist}, Song: {song}"
            
            # Extract using LangExtract
            try:
                result = lx.extract(
                    text_or_documents=track_text,
                    prompt_description=prompt,
                    examples=examples,
                    model_id="gemini-2.0-flash",
                )
                
                # Generate embedding
                embedding_response = self.genai_client.models.embed_content(
                    model=self.embedding_model,
                    contents=[track_text],
                    config=EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=self.embedding_dim,
                    ),
                )
                embedding = embedding_response.embeddings[0].values
                
                # Process extraction results
                primary_genre = "unknown"
                mood = "unknown"
                
                for extraction in result.extractions:
                    if extraction.extraction_class == "music_analysis":
                        attrs = extraction.attributes or {}
                        primary_genre = attrs.get("primary_genre", "unknown")
                        mood = attrs.get("mood", "unknown")
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
                
            except Exception as e:
                print(f"Error processing {artist} - {song}: {e}")
                continue
        
        # Insert into Milvus
        if processed_data:
            self.client.insert(collection_name=self.collection_name, data=processed_data)
            
            # Load collection for querying
            self.client.load_collection(collection_name=self.collection_name)
        
        return {
            "processed_tracks": len(processed_data),
            "total_tracks": len(df)
        }
    
    async def query_music_taste(self, query: str) -> Dict[str, Any]:
        """Process natural language queries about music taste"""
        # Generate query embedding
        query_embedding_response = self.genai_client.models.embed_content(
            model=self.embedding_model,
            contents=[query],
            config=EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=self.embedding_dim,
            ),
        )
        query_embedding = query_embedding_response.embeddings[0].values
        
        # Search for similar tracks
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            anns_field="embedding",
            limit=5,
            output_fields=["track_info", "artist", "song", "primary_genre", "mood"],
            search_params={"metric_type": "COSINE"},
        )
        
        relevant_tracks = []
        if results and results[0]:
            for result in results[0]:
                relevant_tracks.append({
                    "artist": result.get("artist", "Unknown"),
                    "song": result.get("song", "Unknown"),
                    "primary_genre": result.get("primary_genre", "unknown"),
                    "mood": result.get("mood", "unknown"),
                    "similarity_score": 1 - result["distance"]  # Convert distance to similarity
                })
        
        # Generate response using the relevant tracks
        response = await self._generate_response(query, relevant_tracks)
        insights = await self._generate_insights(relevant_tracks)
        
        return {
            "response": response,
            "relevant_tracks": relevant_tracks,
            "insights": insights
        }
    
    async def _generate_response(self, query: str, tracks: List[Dict]) -> str:
        """Generate a natural language response about the music taste"""
        if not tracks:
            return "I don't have enough information about your music taste yet. Please upload your music library first."
        
        # Extract patterns from the tracks
        genres = [track["primary_genre"] for track in tracks]
        moods = [track["mood"] for track in tracks]
        
        genre_counts = Counter(genres)
        mood_counts = Counter(moods)
        
        # Create a simple response based on patterns
        top_genre = genre_counts.most_common(1)[0][0] if genre_counts else "unknown"
        top_mood = mood_counts.most_common(1)[0][0] if mood_counts else "unknown"
        
        response = f"Based on your music library, you seem to have a preference for {top_genre} music with a {top_mood} mood. "
        
        if len(tracks) > 1:
            response += f"Your top matching songs include {tracks[0]['artist']} - {tracks[0]['song']}"
            if len(tracks) > 2:
                response += f" and {tracks[1]['artist']} - {tracks[1]['song']}"
        
        return response
    
    async def _generate_insights(self, tracks: List[Dict]) -> List[str]:
        """Generate insights about music taste patterns"""
        if not tracks:
            return []
        
        insights = []
        
        # Genre insights
        genres = [track["primary_genre"] for track in tracks]
        genre_counts = Counter(genres)
        if len(genre_counts) > 1:
            insights.append(f"Your music spans {len(genre_counts)} different genres")
        
        # Mood insights
        moods = [track["mood"] for track in tracks]
        mood_counts = Counter(moods)
        dominant_mood = mood_counts.most_common(1)[0][0]
        insights.append(f"Your dominant mood preference is {dominant_mood}")
        
        return insights
    
    async def get_library_stats(self) -> Dict[str, Any]:
        """Get statistics about the music library"""
        # Query all tracks
        results = self.client.query(
            collection_name=self.collection_name,
            filter="",
            output_fields=["artist", "song", "primary_genre", "mood"],
            limit=1000
        )
        
        if not results:
            return {
                "total_tracks": 0,
                "genres": {},
                "moods": {},
                "top_artists": []
            }
        
        # Calculate statistics
        genres = [r.get("primary_genre", "unknown") for r in results]
        moods = [r.get("mood", "unknown") for r in results]
        artists = [r.get("artist", "Unknown") for r in results]
        
        genre_counts = dict(Counter(genres))
        mood_counts = dict(Counter(moods))
        artist_counts = Counter(artists)
        
        top_artists = [{"artist": artist, "count": count} 
                      for artist, count in artist_counts.most_common(10)]
        
        return {
            "total_tracks": len(results),
            "genres": genre_counts,
            "moods": mood_counts,
            "top_artists": top_artists
        }
