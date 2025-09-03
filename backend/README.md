# Music Taste Analyzer Backend

A FastAPI backend that uses LangExtract + Milvus integration for music taste analysis.

## Features

- **Music Library Ingestion**: Upload CSV files with artist,song format
- **LangExtract Integration**: Automatically extract genre and mood labels
- **Vector Search**: Semantic search capabilities using Milvus
- **Natural Language Queries**: Chat interface for music taste analysis

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /ingest` - Upload music library CSV
- `POST /chat` - Query music taste with natural language
- `GET /stats` - Get library statistics
- `GET /` - Health check

## CSV Format

Your music library should be a CSV file with this format:
```csv
artist,song
Radiohead,Paranoid Android
Billie Eilish,bad guy
Arctic Monkeys,Do I Wanna Know
```

## Extracted Labels

The system extracts:
- **primary_genre**: rock, pop, hip-hop, electronic, indie, folk, jazz, classical
- **mood**: energetic, chill, melancholic, upbeat, dark, peaceful, aggressive
