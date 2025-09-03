# 🎵 Music Taste Analyzer

An AI-powered music taste analysis app built with **LangExtract + Milvus** integration. Upload your Spotify library and get intelligent insights about your music preferences through natural language queries.

## ✨ Features

- **Smart Music Analysis**: Uses LangExtract to extract genre and mood labels from your music
- **Vector Search**: Semantic search powered by Milvus vector database
- **Natural Language Queries**: Chat interface for questions like "explain my indie rock taste"
- **Visual Statistics**: Genre distribution, mood analysis, and top artists
- **Real Spotify Data**: Designed for actual Spotify listening history

## 🏗️ Architecture

```
Frontend (Next.js) ↔ Backend (FastAPI) ↔ LangExtract ↔ Milvus Vector DB
                                      ↔ Gemini AI
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Clone & Setup

```bash
git clone https://github.com/AkritiKeswani/milvus-music-chat.git
cd milvus-music-chat
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY="your_gemini_api_key_here"
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Using Docker (Optional)

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
docker-compose up
```

## 📊 Your Music Data

### Expected CSV Format
```csv
artist,song
Coldplay,Yellow
OneRepublic,Counting Stars
Morgan Wallen,Last Night
Kygo,Stole the Show
```

### Extracted Labels

**Genres**: pop-rock, indie-folk, country, electronic, alternative, bollywood
**Moods**: melancholic, upbeat, chill, nostalgic, romantic, energetic

## 💬 Example Queries

- "What's my dominant music genre?"
- "Show me my country music vibe"
- "What do I listen to when I'm sad?"
- "Explain my indie rock taste"
- "Find my most energetic songs"

## 🛠️ API Endpoints

- `POST /ingest` - Upload music library CSV
- `POST /chat` - Natural language queries
- `GET /stats` - Library statistics
- `GET /` - Health check

## 📱 Screenshots

Upload your music library → Chat about your taste → View detailed stats

## 🧠 How It Works

1. **Upload**: CSV with artist,song pairs
2. **Extract**: LangExtract analyzes each track for genre/mood
3. **Store**: Milvus stores embeddings + metadata
4. **Query**: Natural language search through your music taste
5. **Insights**: AI-generated analysis of your preferences

## 🔧 Tech Stack

- **Backend**: FastAPI, LangExtract, PyMilvus, Google Gemini
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Database**: Milvus Vector Database
- **AI**: Google Gemini for embeddings and analysis

## 📁 Project Structure

```
milvus-music-chat/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── services/
│   │   └── api/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   └── components/
│   └── package.json
├── sample_music_library.csv
└── docker-compose.yml
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [LangExtract](https://github.com/langchain-ai/langextract) for structured extraction
- [Milvus](https://milvus.io/) for vector database
- [Google Gemini](https://ai.google.dev/) for embeddings and AI analysis

---

**Ready to discover your music taste?** 🎧
