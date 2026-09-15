<div align="center">

# 🎙️ InsightMedia

### ✨ Turn videos and meetings into actionable intelligence

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#-setup)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](#-setup)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-1C3C3C?logo=chainlink&logoColor=white)](#-architecture)
[![ChromaDB](https://img.shields.io/badge/Vector%20Store-ChromaDB-6E56CF)](#-rag)

[![Overview](https://img.shields.io/badge/📌_Overview-00A8E8?style=for-the-badge)](#-project-overview)
[![Features](https://img.shields.io/badge/🚀_Features-3A86FF?style=for-the-badge)](#-features)
[![Architecture](https://img.shields.io/badge/🧩_Architecture-8338EC?style=for-the-badge)](#-architecture)
[![Tech Stack](https://img.shields.io/badge/🛠️_Tech_Stack-FF006E?style=for-the-badge)](#-tech-stack)
[![Setup](https://img.shields.io/badge/⚙️_Setup-FB5607?style=for-the-badge)](#-setup)
[![RAG](https://img.shields.io/badge/🧠_RAG-2A9D8F?style=for-the-badge)](#-rag)

</div>

---

## 📌 Project Overview

**InsightMedia** is an AI video and meeting intelligence assistant that transforms YouTube videos and local audio/video files into useful, structured insights.

### ✨ What it generates

- 🎙️ **Clean Transcripts**
- 🧠 **AI-Generated Titles & Summaries**
- ✅ **Action Items**
- 🔑 **Key Decisions**
- ❓ **Open Questions**
- 💬 **Transcript-Grounded RAG Q&A**

It includes a polished **Streamlit interface** through `app.py` and a complete processing pipeline through `main.py`.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🎬 **Flexible Input** | Process YouTube URLs or local audio/video files |
| 🎙️ **Transcription** | English and Hinglish language modes |
| 🧠 **AI Insights** | Generate titles, summaries and structured insights |
| ✅ **Action Items** | Extract actionable tasks from relevant meeting content |
| 🔑 **Key Decisions** | Identify important confirmed decisions |
| ❓ **Open Questions** | Surface unresolved questions |
| 💬 **RAG Q&A** | Ask questions using the processed transcript as context |

---

## 🧩 Architecture

```text
                         🎬 INPUT
                            │
              ┌─────────────┴─────────────┐
              │                           │
        🔗 YouTube URL              📁 Local File
              │                           │
       Transcript Fetch            🎵 Audio Processing
              │                           │
              │                    ✂️ Chunking
              │                           │
              │                    🎙️ Whisper / Sarvam
              │                           │
              └─────────────┬─────────────┘
                            ↓
                   📝 Clean Transcript
                            │
            ┌───────────────┼───────────────┐
            ↓               ↓               ↓
       🧠 Summary      📊 Extraction    🗄️ ChromaDB
       & Title         & Insights          │
            │               │               ↓
            │               │            🔍 RAG
            │               │               │
            └───────────────┴───────────────┘
                            ↓
                       💬 RAG Q&A
```

---

## 💻 Code Highlights

### 🎙️ Transcription

Local audio/video files are processed using Whisper, with Sarvam AI available for Hinglish transcription.

```python
# core/transcriber.py

model = whisper.load_model(WHISPER_MODEL)

result = model.transcribe(
    audio_path,
    language="en"
)

transcript = result["text"]
```

### 🤖 AI Summarization

Groq is used to generate concise titles and summaries from the transcript.

```python
# core/summarizer.py

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.2,
    max_tokens=500
)

response = llm.invoke(prompt)
```

### 📊 Structured Insight Extraction

The extraction pipeline identifies meeting type, action items, key decisions and open questions.

```python
# core/extractor.py

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.1,
    max_tokens=2000
)

response = llm.invoke(extraction_prompt)
```

### 🧠 RAG & Vector Store

Transcript chunks are converted into embeddings and stored in ChromaDB for contextual question answering.

```python
# core/vector_store.py

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name="transcript",
    embedding_function=embeddings,
    persist_directory="vectore_db"
)
```

### 🔗 Complete Pipeline

The main pipeline connects transcription, AI insights and RAG.

```python
# main.py

transcript = transcribe_all(source)

title = generate_title(transcript)
summary = summarize_text(transcript)

insights = extract_information(transcript)

rag_chain = build_rag_chain(transcript)
```

---

## 🛠️ Tech Stack

### 💻 Core

- 🐍 **Python**
- 🎨 **Streamlit**
- 🔗 **LangChain**

### 🎙️ Transcription

- 🗣️ **OpenAI Whisper** — Local transcription
- 🌐 **Transcript API** — YouTube sources
- 🇮🇳 **Sarvam AI** — Hinglish transcription

### 🤖 AI

- ⚡ **Groq**
- 🧠 **GPT-OSS-20B**
- 🔗 **LangChain LCEL**

### 🧠 RAG

- 🗄️ **ChromaDB**
- 🤗 **HuggingFace Embeddings**
- 🔢 **all-MiniLM-L6-v2**

### 🎵 Media Processing

- 🎞️ **FFmpeg**
- 🔊 **pydub**

---

## ⚙️ Setup

### 1️⃣ Prerequisites

Make sure you have:

- 🐍 Python **3.10+**
- 🎞️ FFmpeg installed and available in PATH

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/meghxx0602/Insight-Media.git
cd Insight-Media
```

### 3️⃣ Create a Virtual Environment

```bash
python -m venv .venv
```

#### 🪟 Windows

```bash
.venv\Scripts\activate
```

#### 🐧 macOS / Linux

```bash
source .venv/bin/activate
```

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 5️⃣ 🔐 Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_key_here
SARVAM_API_KEY=your_key_here
YOUTUBETRANSCRIPT_API_KEY=your_key_here
```

> 🔒 **Never commit your `.env` file or expose API keys publicly.**

### 6️⃣ 🚀 Run the Application

```bash
streamlit run app.py
```

### 🖥️ Optional: Run the Pipeline

```bash
python main.py
```

---

## 🧠 RAG

InsightMedia builds a transcript-specific vector store to support contextual question answering.

### 🔍 How it works

```text
📝 Transcript
      ↓
✂️ Chunking
      ↓
🔢 Embeddings
      ↓
🗄️ ChromaDB
      ↓
🔍 Relevant Context Retrieval
      ↓
🤖 Groq
      ↓
💬 Answer
```

The RAG system retrieves relevant transcript context before generating an answer.

---

## 📁 Project Structure

```text
Insight-Media/
│
├── 🎨 app.py
├── ⚙️ main.py
├── 📦 requirements.txt
├── 🖥️ packages.txt
│
├── 🧠 core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
└── 🛠️ utils/
    └── audio_processor.py
```

---

## ⚠️ Limitations

- 🎙️ Transcription quality depends on audio clarity and content.
- ⏳ Long files can require significant local processing time.
- 🌐 API rate limits may affect generation and Q&A responsiveness.
- 🗣️ Hinglish transcription quality can vary depending on accent and speaking style.
- 🔍 RAG responses depend on the quality of the retrieved transcript context.

---

## 🌱 Future Scope

- 📄 Exportable PDF/Doc reports
- 🎙️ Speaker-aware transcription and insights
- 🌍 Improved multilingual support
- ⚡ Better handling of very long recordings
- 📊 Evaluation and analytics for generated insights

---

## 👤 Author

**Shabana Mallick**

- GitHub: [@meghxx0602](https://github.com/meghxx0602)
- LinkedIn: [Shabana Mallick](https://www.linkedin.com/in/shabana-mallick1220)

---

### Made with ❤️ by Shabana ✿
