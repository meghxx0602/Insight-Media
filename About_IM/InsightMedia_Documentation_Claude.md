# InsightMedia — Complete Project Documentation

InsightMedia is an AI-powered application that takes a YouTube video or a local video/audio file, converts it into a transcript, generates a summary, extracts action items/decisions/questions, and lets the user chat with the video using RAG (Retrieval-Augmented Generation). It has a Streamlit web interface on top of a Python backend pipeline.

This document explains every file in the project, in the order they were built, followed by the complete end-to-end flow.

---

## 1. `.env`

**Purpose:**
Stores all secret API keys and configuration values needed by the project so they are not hardcoded inside the Python files.

**Input:**
None — it is a plain configuration file created manually by the developer.

**What it does:**
- Holds `MISTRAL_API_KEY` (present in the file, though not used by any code shown).
- Holds `WHISPER_MODEL`, which decides the size of the local Whisper model (e.g. `"small"`).
- Holds `SARVAM_API_KEY`, used to authenticate with Sarvam AI's speech-to-text-translate API.
- Holds `GROQ_API_KEY`, used to authenticate with Groq's LLM API (used everywhere an LLM call happens).

**Output:**
Environment variables that become readable through `os.getenv("VAR_NAME")` once loaded.

**Connection / Flow:**
```text
Developer Setup
↓
.env (API keys & config)
↓
load_dotenv() in main.py / app.py
↓
Used inside transcriber.py, summarizer.py, extractor.py, rag_engine.py
```

**Why it is needed:**
Every AI component (Whisper model choice, Sarvam transcription, Groq LLM calls) depends on a key or setting from this file. Without it, none of the API-based files (transcriber, summarizer, extractor, rag_engine) could authenticate.

---

## 2. `requirements.txt`

**Purpose:**
Lists every third-party Python package the project depends on, organized by the stage of the pipeline it supports.

**Input:**
None — it is read by `pip`, not by the application itself.

**What it does:**
- Groups **audio/video acquisition** packages: `yt-dlp`, `pydub`, `ffmpeg-python`.
- Groups **local Speech-to-Text** packages: `openai-whisper`, `torch`, `torchaudio`.
- Groups **translation** package: `deep-translator`.
- Groups **LLM orchestration** packages: `langchain`, `langchain-core`, `langchain-community`, `langchain-groq`, `langchain-chroma`.
- Groups **RAG pipeline** packages: `chromadb`, `sentence-transformers`, `langchain-huggingface`, `huggingface-hub`, `tiktoken`.
- Groups **Streamlit UI** packages: `streamlit`, `streamlit-extras`, `watchdog`.
- Groups **PDF/TXT export** packages: `reportlab`, `fpdf2`.
- Groups **utility** packages: `python-dotenv`, `numpy`, `tqdm`, `requests`.

**Output:**
A fully installed Python environment containing all libraries the project's code imports.

**Connection / Flow:**
```text
Project Setup
↓
requirements.txt (dependency list)
↓
pip install -r requirements.txt
↓
Enables audio_processor.py, transcriber.py, summarizer.py,
extractor.py, vector_store.py, rag_engine.py, app.py to run
```

**Why it is needed:**
Every other file imports one or more of these libraries (`yt_dlp`, `whisper`, `langchain_groq`, `streamlit`, `langchain_chroma`, etc.). Without installing these exact packages, the imports at the top of every file would fail immediately.

---

## 3. `utils/audio_processor.py`

**Purpose:**
Acts as the entry point of the pipeline — it takes either a YouTube URL or a local file path and turns it into a set of clean, standardized audio chunks ready for transcription.

**Input:**
`source: str` — either a YouTube URL (starting with `http://`/`https://`) or a path to a local video/audio file.

**What it does:**
- `download_youtube_audio(url)`: Uses `yt_dlp` to download the best available audio stream from a YouTube URL, then post-processes it into a `.wav` file via FFmpeg.
- `convert_to_wav(input_path)`: Uses `pydub`'s `AudioSegment` to load any local video/audio file, forces it to **mono channel** and **16kHz sample rate** (the format Whisper expects), and exports it as `.wav`.
- `chunk_audio(wav_path, chunk_minutes=10)`: Slices the full WAV file into 10-minute pieces using `pydub` (so long recordings don't have to be transcribed in one giant piece), exporting each piece as its own `.wav` file.
- `process_input(source)`: Decides whether `source` is a URL or a local file, calls the matching function above, then always calls `chunk_audio()` on the result and returns the list of chunk paths.

**Output:**
`chunks: list` — a list of file paths, each pointing to a 10-minute (or shorter, for the last piece) `.wav` audio chunk.

**Connection / Flow:**
```text
User Input (YouTube URL / Local File)
↓
audio_processor.py
↓
List of WAV audio chunks
↓
transcriber.py
```

**Why it is needed:**
It normalizes two very different kinds of input (an online video link vs. a local file in any format) into one consistent output format (chunked, mono, 16kHz WAV files) that every downstream AI component can rely on.

---

## 4. `core/transcriber.py`

**Purpose:**
Converts the audio chunks produced by `audio_processor.py` into actual text, supporting two transcription engines depending on the spoken language, and lightly cleans up the resulting text.

**Input:**
`chunks: list` (audio chunk paths from `audio_processor.py`) and `language: str` (`"english"` or `"hinglish"`).

**What it does:**
- `load_model()`: Loads the local Whisper model (size controlled by `WHISPER_MODEL` env variable) only once, caching it in a global `_model` variable so it isn't reloaded for every chunk.
- `transcribe_chunk_whisper(chunk_path)`: Runs Whisper's `.transcribe()` on one chunk for **English** audio and returns the text.
- `transcribe_chunk_sarvam(chunk_path)` / `_send_to_sarvam(piece_path)`: Because Sarvam's sync API only accepts audio ≤30 seconds, this splits each 10-minute chunk into 25-second pieces, sends each piece to Sarvam's `speech-to-text-translate` endpoint via `requests.post`, and joins the returned English transcripts — used for **Hinglish** audio (it translates while transcribing).
- `transcribe_chunk(chunk_path, language)`: Router function — picks Whisper for `"english"` and Sarvam for `"hinglish"`.
- `transcribe_all(chunks, language)`: Loops through every chunk, transcribes each one, and concatenates everything into one long transcript string.
- `clean_transcript(text)`: Applies regex-based cleanup — collapses immediate repeated words/phrases (a common Whisper artifact), strips filler words (`um`, `uh`, `you know`, `i mean`, etc.), and normalizes extra whitespace. No LLM is used for this step.

**Output:**
A single cleaned transcript string (the full text of the video/meeting).

**Connection / Flow:**
```text
audio_processor.py (WAV chunks)
↓
transcriber.py
↓
Cleaned Full Transcript (text)
↓
summarizer.py / extractor.py / vector_store.py
```

**Why it is needed:**
This is the bridge between raw audio and text. Every AI feature downstream — summary, action items, decisions, questions, and RAG chat — depends entirely on the transcript this file produces.

---

## 5. `core/summarizer.py`

**Purpose:**
Uses Groq's LLM to generate a short title and a concise bullet-point summary of the transcript.

**Input:**
`transcript: str` — the full cleaned transcript from `transcriber.py`.

**What it does:**
- `get_llm()`: Initializes a `ChatGroq` model (`openai/gpt-oss-20b`) using `GROQ_API_KEY`, with low `temperature=0.2` for more consistent, less random output.
- `generate_title(transcript)`: Sends the first 3000 characters of the transcript to the LLM with a strict prompt (max 8 words, use only transcript info, no questions, no invented content), and returns just the first line of the response. Falls back to `"Meeting Discussion"` on error or empty output.
- `split_transcript(transcript)`: Uses `RecursiveCharacterTextSplitter` (chunk size 3000, overlap 200) to break a long transcript into manageable pieces, since an LLM call can't process unlimited text at once.
- `summarize_chunk(chunk)`: Sends one chunk to the LLM with a strict system prompt (own words, no copying, no filler, 2–4 bullet points, only important ideas) and returns the bullet-point response for that chunk.
- `summarize(transcript)`: Splits the transcript, summarizes every chunk, merges all bullet lines together, strips bullet symbols, removes duplicate points (case-insensitively), caps the result to a maximum of 8 points, and returns them as a formatted bullet list.

**Output:**
`title: str` and `summary: str` (a markdown-style bullet list, max 8 points).

**Connection / Flow:**
```text
transcriber.py (Full Transcript)
↓
summarizer.py
↓
Title + Summary (bullet points)
↓
main.py (added to result dict) → app.py (displayed to user)
```

**Why it is needed:**
It gives the user an instant, digestible overview of the video/meeting without needing to read the entire transcript.

---

## 6. `core/extractor.py`

**Purpose:**
Extracts structured information from the transcript — action items, key decisions, and open questions — and first checks whether the content is even meeting-like content at all.

**Input:**
`transcript: str` — the full cleaned transcript.

**What it does:**
- `get_llm()`: Initializes `ChatGroq` (`openai/gpt-oss-20b`) with a very low `temperature=0.1` and `reasoning_effort="low"`, favoring precise, deterministic extraction over creativity.
- `classify_content_type(transcript)`: Sends the first 1500 characters to the LLM asking it to classify the content as `MEETING` or `NOT_MEETING` (e.g. lectures/tutorials/documentaries are `NOT_MEETING`). This avoids inventing fake action items for content that was never a discussion.
- `split_transcript(transcript)`: Splits the transcript into chunks (size 2200, overlap 150) for the same reason as in `summarizer.py` — LLM calls need manageable input sizes.
- `extract_from_chunk(chunk)`: Sends a very detailed, strict prompt to the LLM asking it to return JSON with `action_items`, `key_decisions`, and `open_questions` — including explicit rules for telling a real decision apart from a mere proposal, and a real open question apart from a rhetorical one. Strips markdown code fences if the model wraps the JSON in them, then parses it with `json.loads`. Returns empty lists on any error.
- `extract_all(transcript)`: Loops through all chunks, calls `extract_from_chunk` on each, and aggregates every category's results across all chunks.
- `remove_duplicates`, `format_action_item`, `format_action_items`, `format_decisions`, `format_questions`: Clean, de-duplicate (case-insensitive), and format the raw extracted lists into numbered, human-readable text blocks. Questions are additionally filtered to only keep strings containing a `?`.
- `extract_information(transcript)`: The main entry point — first classifies the content type. If it's `NOT_MEETING`, it skips extraction entirely and returns placeholder "not found" messages. Otherwise, it runs the full extraction and formatting pipeline.

**Output:**
A dictionary: `{"action_items": str, "key_decisions": str, "open_questions": str}` (each is formatted, numbered text, or a "none found" message).

**Connection / Flow:**
```text
transcriber.py (Full Transcript)
↓
extractor.py
↓
Action Items + Key Decisions + Open Questions (formatted text)
↓
main.py (added to result dict) → app.py (displayed to user)
```

**Why it is needed:**
It converts an unstructured transcript into concrete, actionable outputs, saving the user from manually scanning the whole conversation to find tasks, agreements, and unresolved points.

---

## 7. `core/vector_store.py`

**Purpose:**
Builds and manages a local ChromaDB vector database that stores the transcript as searchable embeddings — this is the foundation of the RAG (chat) feature.

**Input:**
`transcript: str` (to build/load a store), and later a `vector_store` object (to get a retriever).

**What it does:**
- `get_embeddings()`: Loads the HuggingFace embedding model `all-MiniLM-L6-v2`, configured to run on CPU, which converts text into numerical vectors.
- `get_collection_name(transcript)`: Hashes the transcript text using MD5 (first 12 hex characters) to build a unique, deterministic collection name (e.g. `meeting_ab12cd34ef56`) — so the same transcript always maps to the same ChromaDB collection.
- `build_vector_store(transcript)`: Splits the transcript into small chunks (size 500, overlap 50) via `RecursiveCharacterTextSplitter`, wraps each chunk into a LangChain `Document` (with a `chunk_index` in its metadata), embeds all of them, and stores them in a persistent Chroma collection saved to the local `vectore_db` folder.
- `load_vector_store(transcript)`: Reconnects to an already-existing persisted Chroma collection for the same transcript (matched via the same hash), without rebuilding the embeddings from scratch.
- `get_retriever(vector_store, k=4)`: Wraps a vector store as a retriever configured for similarity search, returning the top-`k` most relevant chunks for a given query.

**Output:**
A `Chroma` vector store object, and from `get_retriever`, a retriever object that can fetch relevant chunks.

**Connection / Flow:**
```text
transcriber.py (Full Transcript)
↓
vector_store.py
↓
Embedded transcript chunks stored in ChromaDB (persisted locally)
↓
rag_engine.py
```

**Why it is needed:**
This is what makes "RAG" possible — instead of feeding the entire (possibly very long) transcript to the LLM for every question, the transcript is pre-embedded and indexed so only the most relevant chunks are retrieved and sent to the LLM.

---

## 8. `core/rag_engine.py`

**Purpose:**
Builds the actual Retrieval-Augmented Generation (RAG) chain that powers the "chat with your video" feature, ensuring answers come only from the transcript content.

**Input:**
`transcript: str` (to build or load the chain), and `question: str` (at query time, via `ask_question`).

**What it does:**
- `get_llm()`: Sets up `ChatGroq` with the same model (`openai/gpt-oss-20b`).
- `format_docs(docs)`: Converts the list of retrieved `Document` objects into a single combined string (joining each chunk's `page_content` with blank lines), so it can be inserted into the LLM prompt as context.
- `build_rag_chain(transcript)`: Calls `build_vector_store(transcript)` to create the embeddings the first time, gets a retriever (`k=10`), defines a very strict system prompt (answer only from context, never invent info, carefully distinguish an accepted decision from a mere proposal), and assembles the full pipeline using LangChain's LCEL (`|` pipe) syntax: `{context: retriever → format_docs, question: passthrough} → prompt → llm → StrOutputParser`.
- `load_rag_chain(transcript)`: Identical to `build_rag_chain`, except it calls `load_vector_store()` instead of `build_vector_store()`, reusing an already-existing database rather than rebuilding it.
- `ask_question(rag_chain, question)`: Invokes the chain with the user's question and returns the answer; catches exceptions and returns a friendly fallback message for rate-limit (HTTP 429) errors or any other failure.

**Output:**
A runnable `rag_chain` object (from the build/load functions), and an `answer: str` (from `ask_question`).

**Connection / Flow:**
```text
vector_store.py (ChromaDB retriever)
↓
rag_engine.py
↓
RAG Chain (retriever + strict prompt + Groq LLM)
↓
app.py (Chat page) → User receives a grounded answer
```

**Why it is needed:**
It is the AI "brain" behind the chat feature — it lets the user ask free-form questions about their video and get answers that are grounded strictly in the transcript, instead of the LLM guessing or hallucinating.

---

## 9. `main.py`

**Purpose:**
Orchestrates the entire InsightMedia pipeline end-to-end, connecting every module into one callable function, and provides a command-line entry point for testing outside the web app.

**Input:**
`source: str` (YouTube URL or local file path) and `language: str` (`"english"` or `"hinglish"`, default `"english"`).

**What it does:**
- Calls `load_dotenv()` at import time to load the API keys from `.env`.
- `run_pipeline(source, language)`:
  1. Calls `process_input(source)` from `audio_processor.py` → gets audio chunks.
  2. Calls `transcribe_all(chunks, language)` from `transcriber.py` → gets the full transcript.
  3. Calls `generate_title(transcript)` and `summarize(transcript)` from `summarizer.py` → gets title and summary.
  4. Calls `extract_information(transcript)` from `extractor.py` → gets action items, decisions, and questions.
  5. Calls `build_rag_chain(transcript)` from `rag_engine.py` → gets a ready-to-use RAG chain.
  6. Packages everything into one result dictionary and returns it.
- `if __name__ == "__main__":` block — a CLI entry point: asks the user for a source and language via `input()`, runs the pipeline, prints the title/summary/action items/decisions/questions, then opens an interactive terminal loop where the user can type questions and get answers via `ask_question()` until they type `exit`/`quit`/`q`.

**Output:**
A dictionary: `{title, transcript, summary, action_items, key_decisions, open_questions, rag_chain}`.

**Connection / Flow:**
```text
audio_processor.py + transcriber.py + summarizer.py + extractor.py + rag_engine.py
↓
main.py (run_pipeline)
↓
Combined result dict (title, transcript, summary, action items, decisions, questions, rag_chain)
↓
app.py (Streamlit UI) or CLI terminal output
```

**Why it is needed:**
It is the central orchestrator — without it, each module would remain a disconnected piece. `main.py` defines the exact order the pipeline runs in and exposes one simple function, `run_pipeline`, that both the CLI mode and the Streamlit app (`app.py`) call to get results.

---

## 10. `app.py`

**Purpose:**
The Streamlit web interface for InsightMedia — the user-facing layer that lets people upload/paste a video, view the AI-generated insights, and chat with the video, all inside a browser.

**Input:**
User interactions: a YouTube URL or an uploaded file, a selected language, button clicks, and typed chat questions.

**What it does:**
- Loads `.env` and imports `run_pipeline` from `main.py` and `ask_question` from `core/rag_engine.py`.
- Configures the Streamlit page (title, icon, wide layout) and injects custom CSS for the header, result cards, and chat box styling.
- Initializes `st.session_state` values (`result`, `source_name`, `messages`) so data survives Streamlit's automatic reruns.
- Builds a sidebar with navigation between three pages — **Home**, **New Analysis**, **Chat (RAG)** — plus a feature list.
- **New Analysis page:** lets the user pick "YouTube URL" or "Local File" (saved to a temp directory on upload), choose a language, and click "Analyze Video." This triggers `run_pipeline(source, language)` inside a `st.status(...)` block (with step messages like "Transcribing with Whisper..."), storing the returned result in `st.session_state.result`, with a try/except to show a friendly error if anything fails.
- **Results display:** once a result exists, shows the title, summary, action items, key decisions, open questions (each in styled containers/columns), and the full transcript inside an expandable section.
- **Chat (RAG) page:** shows the existing chat history, takes new questions through `st.chat_input`, calls `ask_question(rag_chain, question)` on the RAG chain stored in the result, and appends both the user's question and the AI's answer to `st.session_state.messages` so the conversation persists and re-renders on screen.

**Output:**
A fully interactive browser-based web application — visual result cards and a live chat interface.

**Connection / Flow:**
```text
main.py (run_pipeline result: title, summary, action items,
          decisions, questions, rag_chain)
↓
app.py (Streamlit UI)
↓
Visual Results + Interactive Chat
↓
End User (browser)
```

**Why it is needed:**
It turns the whole backend AI pipeline into an accessible, no-code product. Without it, a user would have to run `main.py` from a terminal and type everything manually — `app.py` is what makes InsightMedia usable as an actual application.

---

# Complete Project Flow

```text
                              USER INPUT
                    (YouTube URL or Local File + Language)
                                  │
                                  ▼
                       utils/audio_processor.py
              (download/convert audio → chunk into WAV pieces)
                                  │
                                  ▼
                         core/transcriber.py
        (Whisper for English / Sarvam for Hinglish → clean transcript)
                                  │
                 ┌────────────────┼──────────────────┐
                 ▼                ▼                   ▼
     core/summarizer.py   core/extractor.py    core/vector_store.py
   (title + bullet summary) (action items, key    (chunk transcript →
                              decisions, open        embed → store in
                              questions)              ChromaDB)
                 │                │                   │
                 │                │                   ▼
                 │                │          core/rag_engine.py
                 │                │        (retriever + prompt + LLM
                 │                │             = RAG chain)
                 │                │                   │
                 └────────────────┴───────────────────┘
                                  │
                                  ▼
                              main.py
                (run_pipeline: combines everything into
                 one result dict — title, transcript, summary,
                 action items, decisions, questions, rag_chain)
                                  │
                                  ▼
                              app.py
                (Streamlit UI: shows results, runs the pipeline
                 on button click, hosts the RAG chat page)
                                  │
                                  ▼
                              END USER
                (sees title/summary/action items/decisions/
                 questions, and can chat with the video via RAG)
```

---

# Detailed End-to-End Flow

1. **User provides input** in `app.py` — either a YouTube URL or an uploaded local video/audio file, plus a language choice (`english`/`hinglish`). Clicking "Analyze Video" calls `run_pipeline(source, language)` from `main.py`.

2. **`main.py` → `audio_processor.py`:** `process_input(source)` receives the raw source. If it's a URL, `download_youtube_audio()` downloads and converts it to WAV via `yt_dlp`/FFmpeg. If it's a local file, `convert_to_wav()` uses `pydub` to force it to mono, 16kHz WAV. Either way, `chunk_audio()` then slices the WAV into 10-minute pieces. **Output:** a list of chunk file paths.

3. **`main.py` → `transcriber.py`:** `transcribe_all(chunks, language)` receives the chunk list. For each chunk, `transcribe_chunk()` routes to either `transcribe_chunk_whisper()` (local Whisper model, for English) or `transcribe_chunk_sarvam()` (splits into 25s pieces and calls the Sarvam API, for Hinglish). All chunk transcripts are joined, then `clean_transcript()` removes repeated words and filler words. **Output:** one clean transcript string.

4. **`main.py` → `summarizer.py`:** `generate_title(transcript)` and `summarize(transcript)` each receive the transcript. The title generator asks the Groq LLM for a short title from the first 3000 characters. The summarizer splits the transcript into 3000-character chunks, summarizes each with the LLM into bullet points, then merges, deduplicates, and caps the result at 8 bullet points. **Output:** a title string and a summary string.

5. **`main.py` → `extractor.py`:** `extract_information(transcript)` receives the transcript. It first classifies the content as `MEETING` or `NOT_MEETING` using the LLM. If it's a meeting, the transcript is split into 2200-character chunks, and each chunk is sent to the LLM with a strict prompt to extract action items, key decisions, and open questions as JSON. Results from all chunks are merged, deduplicated, and formatted into readable numbered text. **Output:** three formatted strings — action items, key decisions, open questions.

6. **`main.py` → `vector_store.py` (via `rag_engine.py`):** `build_rag_chain(transcript)` calls `build_vector_store(transcript)`, which splits the transcript into small 500-character chunks, embeds them using the `all-MiniLM-L6-v2` HuggingFace model, and stores them in a local persistent ChromaDB collection (named from an MD5 hash of the transcript).

7. **`rag_engine.py` builds the RAG chain:** it wraps the ChromaDB collection as a retriever (`k=10`), defines a strict system prompt that forces the LLM to answer only from retrieved context, and chains `retriever → format_docs → prompt → Groq LLM → StrOutputParser` using LangChain's LCEL syntax. **Output:** a ready-to-use `rag_chain` object (no question asked yet).

8. **`main.py` collects everything:** title, transcript, summary, action_items, key_decisions, open_questions, and rag_chain are packaged into a single dictionary and returned to whichever caller invoked `run_pipeline` (either the Streamlit app or the CLI block in `main.py` itself).

9. **`app.py` displays the results:** the returned dictionary is stored in `st.session_state.result`. The "New Analysis" page then renders the title, summary, action items, key decisions, open questions, and a collapsible full transcript.

10. **`app.py` handles the chat:** on the "Chat (RAG)" page, the user types a question into `st.chat_input`. `ask_question(rag_chain, question)` (from `rag_engine.py`) is called — it invokes the stored `rag_chain`, which retrieves the top-10 most relevant transcript chunks from ChromaDB, feeds them plus the question into the Groq LLM through the strict prompt, and returns a grounded answer. Both the question and answer are appended to `st.session_state.messages` and displayed as chat bubbles.

---

# One-Line Summary

| File | One-Line Summary |
|---|---|
| `.env` | Stores the API keys and settings every other file needs to run. |
| `requirements.txt` | Lists all the Python libraries the project depends on. |
| `utils/audio_processor.py` | Turns a YouTube link or local file into chunked WAV audio. |
| `core/transcriber.py` | Converts audio chunks into a clean text transcript (Whisper or Sarvam). |
| `core/summarizer.py` | Generates a short title and bullet-point summary from the transcript. |
| `core/extractor.py` | Extracts action items, key decisions, and open questions from the transcript. |
| `core/vector_store.py` | Splits and embeds the transcript into a searchable ChromaDB vector database. |
| `core/rag_engine.py` | Builds the RAG chain that answers user questions using only the transcript. |
| `main.py` | Runs the full pipeline end-to-end and exposes it as one function. |
| `app.py` | The Streamlit web app where the user uploads a video and chats with it. |

---

# Final Project Summary

InsightMedia lets a user take any YouTube video or local video/audio file and turn it into structured, searchable knowledge — without watching or reading the whole thing.

In simple terms: the user gives a video (link or file) and a language choice to the Streamlit app (`app.py`). Behind the scenes, `main.py` runs the pipeline in order — `audio_processor.py` turns the video into chunked audio, `transcriber.py` turns that audio into text (using Whisper for English or Sarvam for Hinglish), and that transcript becomes the single source of truth for everything that follows. From the transcript, `summarizer.py` produces a short title and bullet summary, `extractor.py` pulls out action items, decisions, and open questions (while first checking if the content is even meeting-like), and `vector_store.py` breaks the transcript into small pieces and stores them as searchable embeddings in a local ChromaDB database. `rag_engine.py` then wraps that database in a RAG chain, so any question the user later asks is answered by retrieving only the most relevant transcript pieces and passing them to the Groq LLM — keeping answers grounded in what was actually said rather than invented.

Finally, `app.py` ties it all together visually: it runs the pipeline when the user clicks "Analyze Video," displays the title/summary/action items/decisions/questions, and provides a chat page where the user can ask free-form questions and get transcript-grounded AI answers through the RAG chain. The end result is that a user gets both a quick AI-generated overview of their video/meeting and an interactive Q&A assistant that knows only what was said in that specific video.
