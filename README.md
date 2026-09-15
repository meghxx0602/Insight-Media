<div align="center">

# 🎙️ InsightMedia
### Turn videos and meetings into actionable intelligence

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#-setup)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](#-setup)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-1C3C3C?logo=chainlink&logoColor=white)](#-architecture)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-6E56CF)](#-rag)
[![License](https://img.shields.io/badge/License-MIT-green)](#)

[![Overview](https://img.shields.io/badge/Overview-00A8E8?style=for-the-badge)](#-project-overview)
[![Features](https://img.shields.io/badge/Features-3A86FF?style=for-the-badge)](#-features)
[![Architecture](https://img.shields.io/badge/Architecture-8338EC?style=for-the-badge)](#-architecture)
[![Tech%20Stack](https://img.shields.io/badge/Tech%20Stack-FF006E?style=for-the-badge)](#-tech-stack)
[![Setup](https://img.shields.io/badge/Setup-FB5607?style=for-the-badge)](#-setup)
[![RAG](https://img.shields.io/badge/RAG-2A9D8F?style=for-the-badge)](#-rag)

</div>

## 📌 Project Overview

InsightMedia is an AI-powered video and meeting intelligence assistant that converts YouTube/local media into:
- clean transcripts
- concise summaries
- action items
- key decisions
- open questions
- transcript-grounded Q&A with RAG

It includes a polished Streamlit UI (`app.py`) and a CLI pipeline (`main.py`).

## 🚀 Features

- 🎬 Input support: YouTube URL or local audio/video file
- 🎙️ Transcription with language mode selection (`english`, `hinglish`)
- 🧠 AI-generated title and structured summary
- ✅ Automatic extraction of action items
- 🔑 Detection of confirmed key decisions
- ❓ Identification of unresolved open questions
- 💬 RAG chat that answers only from the processed transcript context

## 🧩 Architecture

```text
Input (YouTube URL / Local File)
        │
        ├─ YouTube URL → Transcript fetch → Clean transcript
        └─ Local File  → WAV conversion + chunking → Transcription → Clean transcript
                          │
                          ├─ Title generation
                          ├─ Summary generation
                          ├─ Action/Decision/Question extraction
                          └─ Vector store (ChromaDB) + Retriever + LLM
                                                     │
                                                     └─ RAG Q&A
```

## 🛠 Tech Stack

- **Language:** Python
- **UI:** Streamlit
- **Transcription:** OpenAI Whisper (local), API-based transcript/translation flow for supported sources
- **LLM orchestration:** LangChain (LCEL), LangChain Groq
- **RAG:** ChromaDB, HuggingFace embeddings (`all-MiniLM-L6-v2`)
- **Media processing:** pydub, ffmpeg

## ⚙️ Setup

### 1) Prerequisites
- Python 3.10+
- FFmpeg installed and available in PATH

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment
Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_key_here
SARVAM_API_KEY=your_key_here
YOUTUBETRANSCRIPT_API_KEY=your_key_here
```

### 4) Run the app

```bash
streamlit run app.py
```

### 5) Run CLI mode (optional)

```bash
python main.py
```

## 🔎 RAG

InsightMedia builds a transcript-specific vector store and uses retrieval + LLM answering to keep responses grounded in meeting/video context.

- Transcript is chunked and embedded
- Chunks are stored in ChromaDB
- Top-k relevant chunks are retrieved per question
- Final answer is generated strictly from retrieved transcript context

## 📁 Project Structure

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

## ⚠️ Limitations

- Performance and quality depend on input audio clarity
- Long files can increase processing time
- API rate limits may affect generation or chat responsiveness
- Hinglish/translated transcript quality may vary by content style and accent

## 🌱 Future Scope

- Exportable reports (PDF/Doc) from analysis output
- Better handling for very long recordings and batch workflows
- Improved multilingual support and transcript post-processing
- Enhanced analytics dashboard for insight trends

## 👤 Author

**Shabana Mallick**

- GitHub: <a href="https://github.com/meghxx0602">@meghxx0602</a>
- LinkedIn: <a href="https://www.linkedin.com/in/shabana-mallick1220">Shabana Mallick</a>

---

### Made with ❤️ by Shabana ✿
