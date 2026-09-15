# 🎙️ Insight Media

**AI-powered video and meeting intelligence tool** that converts YouTube links or local media into clean transcripts, concise summaries, structured insights, and searchable Q&A.

---

## 📌 Project Overview
Insight Media helps turn long-form audio/video content into actionable outputs for learning, documentation, and decision-making. It supports two input modes: direct YouTube transcript fetching and local file transcription, followed by summarization, insight extraction, and RAG-based querying.

## 🚀 Features
- YouTube URL and local file support
- Transcript cleanup and normalization
- AI-generated title and summary
- Extraction of action items, key decisions, and open questions
- ChromaDB-backed RAG for contextual Q&A
- Streamlit interface with multi-page workflow

## 🧩 Architecture
```text
Input (YouTube URL / Local File)
        │
        ├─ YouTube URL → Transcript fetch ───────┐
        │                                        │
        └─ Local File → WAV → Chunking → STT ───┤
                                                 ↓
                                         Clean Transcript
                                                 │
                         ┌───────────────────────┼───────────────────────┐
                         ↓                       ↓                       ↓
                  Title + Summary       Insight Extraction        ChromaDB + RAG
                         │                       │                       │
                         └───────────────────────┴───────────────────────┘
                                                 ↓
                                              RAG Q&amp;A
```

## 🛠 Tech Stack
- **Python**
- **Streamlit**
- **LangChain (LCEL)**
- **Groq API (`openai/gpt-oss-20b`)**
- **Whisper (local STT)**
- **Sarvam STT Translate API** (for Hinglish flow)
- **ChromaDB**
- **HuggingFace Embeddings** (`all-MiniLM-L6-v2`)
- **FFmpeg + pydub**

## ⚙️ Setup
1. Clone the repository and move into the project root.
2. Create and activate a Python 3.10+ virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Add a `.env` file in `/home/runner/work/Insight-Media/Insight-Media` with:
   ```env
   GROQ_API_KEY=your_key_here
   YOUTUBE_TRANSCRIPT_API_KEY=your_key_here
   SARVAM_API_KEY=your_key_here
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## 🔎 RAG
Insight Media builds transcript chunks, embeds them, stores vectors in ChromaDB, and retrieves the most relevant context for question answering. Responses are constrained to transcript-backed evidence to reduce hallucinations.

## 📁 Project Structure
```text
Insight-Media/
├── app.py
├── main.py
├── requirements.txt
├── packages.txt
├── core/
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── extractor.py
│   ├── vector_store.py
│   └── rag_engine.py
└── utils/
    └── audio_processor.py
```

## ⚠️ Limitations
- Output quality depends on transcript quality and audio clarity.
- API rate limits or missing keys can interrupt processing.
- Hinglish support depends on external STT translation behavior.
- Very large files can increase processing latency.

## 🌱 Future Scope
- Speaker diarization and timeline-aligned insights
- Export options for structured reports and notes
- Better multilingual coverage and domain-tuned prompts
- Evaluation dashboards for summary and extraction quality

## 👤 Author
**Megha**
- GitHub: [@meghxx0602](https://github.com/meghxx0602)
- LinkedIn: [Megha](https://www.linkedin.com/)
