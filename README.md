# InsightMedia
**AI-powered video and meeting intelligence from raw media to actionable insights.**

InsightMedia processes a YouTube URL or local video/audio file, generates a clean transcript, summarizes key points, extracts structured meeting outcomes, and enables transcript-grounded Q&A through a Retrieval-Augmented Generation (RAG) pipeline.

## Key Features
- **Flexible input**: analyze either YouTube links or local media files.
- **Automatic transcription pipeline**: converts media to WAV, chunks audio, and transcribes content.
- **AI-generated insights**:
  - concise summary
  - action items
  - key decisions
  - open questions
- **RAG chat**: ask follow-up questions answered only from transcript context.
- **Dual interfaces**:
  - Streamlit web app (`app.py`)
  - CLI workflow (`main.py`)
- **Persistent local vector store** for transcript retrieval.

## Architecture / Workflow
1. Input source selected (YouTube URL or local file)
2. Local file path:
   - media converted to WAV
   - WAV split into chunks
   - chunks transcribed
3. YouTube URL:
   - transcript fetched via external transcript API
4. Transcript cleanup
5. LLM-based title generation and summarization
6. Structured extraction (action items, decisions, questions)
7. Transcript chunking + embeddings + Chroma vector index
8. RAG chain answers user questions with retrieved transcript context

## Tech Stack
- **Language**: Python
- **UI**: Streamlit
- **LLM orchestration**: LangChain (core/community/groq/chroma/huggingface)
- **Model endpoint**: Groq API
- **Speech & media**: Whisper, pydub, yt-dlp, ffmpeg
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Utilities**: python-dotenv, requests, tqdm, numpy

## Project Structure
```text
Insight-Media/
├── app.py
├── main.py
├── requirements.txt
├── packages.txt
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
└── utils/
    └── audio_processor.py
```

## Installation & Setup
### 1) Clone and enter the project
```bash
git clone https://github.com/meghxx0602/Insight-Media.git
cd Insight-Media
```

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
# .venv\Scripts\activate      # Windows (PowerShell)
```

### 3) Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4) Install system dependency
`ffmpeg` is required for media conversion and chunking.

## Environment Variables
Create a `.env` file in the repository root:

```env
GROQ_API_KEY=your_groq_api_key_here
YOUTUBETRANSCRIPT_API_KEY=your_transcript_api_key_here
SARVAM_API_KEY=your_stt_translate_api_key_here
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

> Keep keys private and never commit `.env` to version control.

## Run the App
### Streamlit UI
```bash
streamlit run app.py
```

### CLI Mode
```bash
python main.py
```

## RAG Q&A (How it works)
- The transcript is split into smaller chunks.
- Each chunk is converted into embeddings and stored in a local Chroma collection.
- For each question, the retriever fetches the most relevant transcript chunks.
- The LLM answers using only retrieved transcript context (no external knowledge intended).

## Current Limitations
- Best suited for **English/Hinglish** workflows as currently implemented.
- Relies on external APIs and model endpoints; rate limits or downtime can affect processing.
- Processing can be slow for long files due to chunked transcription and summarization.
- Vector store is local; no multi-user/session persistence layer.
- No automated test suite is currently included in this repository.

## Future Scope
- Background job handling and progress persistence for large media files.
- Better observability (structured logs, telemetry, error traces).
- Export/shareable reports for summaries and extracted outcomes.
- Improved speaker-aware insights and richer meeting analytics.
- Containerized deployment and production-ready configuration options.

## Author
**Shabana**  
Built with Python, Streamlit, and LangChain for practical AI-driven media understanding.
