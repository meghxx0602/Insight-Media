Bhai, ek important thing first: **you pasted live-looking API keys in the message.** I won’t reproduce them in the documentation. You should **rotate/revoke those keys and replace them in `.env`** before sharing the project anywhere.

I’ve treated the code you provided as the source of truth. I’m also keeping the creation order you gave, including `vector_store.py` between `extractor.py` and `rag_engine.py`.

# 🎙️ InsightMedia — Complete Project Documentation

## Project Overview

InsightMedia is an AI-powered video and meeting intelligence application.

It accepts either a **YouTube URL or a local audio/video file**, processes the audio, converts speech into text, generates AI-based insights, extracts structured information, creates a searchable vector store, and allows the user to ask questions about the processed content using RAG.

The project is divided into:

* Environment/configuration
* Dependency setup
* Audio/video processing
* Transcription
* AI summarization
* Information extraction
* Vector database creation
* RAG question answering
* Pipeline coordination
* Streamlit user interface

---

# 1. `.env`

## Purpose:

The `.env` file stores configuration values and API keys used by different parts of InsightMedia.

It keeps these values outside the Python source files.

## Input:

The file itself does not receive input from another Python file.

It contains environment variables such as:

* `MISTRAL_API_KEY`
* `WHISPER_MODEL`
* `SARVAM_API_KEY`
* `GROQ_API_KEY`

The actual secret values are intentionally not reproduced here.

## What it does:

1. Stores the Whisper model selection, currently configured as `small`.
2. Stores the Sarvam API key used by the Sarvam speech-to-text/translation API.
3. Stores the Groq API key used by the Groq LLM.
4. Stores a Mistral API key, although the provided project code does not currently use it.

## Output:

The `.env` file does not directly return anything.

When `load_dotenv()` is called, these values become available as environment variables that Python code can access using `os.getenv()`.

## Connection / Flow:

```text
.env
↓
load_dotenv()
↓
Environment variables
↓
transcriber.py / summarizer.py / extractor.py / rag_engine.py
```

## Why it is needed:

Different components need API keys and configuration values without hardcoding them directly into the Python files.

---

# 2. `requirements.txt`

## Purpose:

`requirements.txt` contains the Python packages required to run InsightMedia.

## Input:

It receives no runtime input.

It is used during project setup to install the required Python libraries.

## What it does:

The requirements cover several parts of the application:

### Audio / Video

* `yt-dlp` — downloads audio from YouTube.
* `pydub` — processes and converts audio.
* `ffmpeg-python` — provides Python bindings for FFmpeg.

### Speech-to-Text

* `openai-whisper` — runs Whisper locally.
* `torch` — backend used by Whisper.
* `torchaudio` — audio utilities for PyTorch.

### Translation

* `deep-translator` — translation support.

### LangChain / Groq

* `langchain`
* `langchain-core`
* `langchain-community`
* `langchain-groq`
* `langchain-chroma`

These provide the LLM and orchestration functionality used by the project.

### RAG / Vector Database

* `chromadb`
* `sentence-transformers`
* `langchain-huggingface`
* `huggingface-hub`
* `tiktoken`

These support embeddings, vector storage and retrieval.

### Streamlit

* `streamlit`
* `streamlit-extras`
* `watchdog`

These support the user interface and Streamlit runtime.

### Export / Utilities

* `reportlab`
* `fpdf2`
* `python-dotenv`
* `numpy`
* `tqdm`
* `requests`

## Output:

The result is an environment containing the Python dependencies required by InsightMedia.

The project also requires the **FFmpeg binary separately**, because `ffmpeg-python` is only the Python binding.

The `yt-dlp` configuration in the provided code also specifies a **Deno JavaScript runtime**.

## Connection / Flow:

```text
requirements.txt
↓
pip install -r requirements.txt
↓
Python libraries installed
↓
InsightMedia files can import and use them
```

## Why it is needed:

Without these dependencies, files such as `audio_processor.py`, `transcriber.py`, `summarizer.py`, `vector_store.py`, `rag_engine.py`, and `app.py` cannot run.

---

# 3. `utils/audio_processor.py`

## Purpose:

This file prepares the user's audio/video input for transcription.

Its main responsibility is to turn either a YouTube URL or local media file into **WAV audio chunks** that the transcription system can process.

## Input:

It receives:

```text
YouTube URL
OR
Local audio/video file path
```

The main function receiving this is:

```python
process_input(source)
```

## What it does:

### 1. Creates the download directory

The file creates a `downloads` directory if it does not already exist.

```text
downloads/
```

### 2. Handles YouTube URLs

If the input starts with `http://` or `https://`, the file treats it as a YouTube URL.

`yt-dlp` downloads the best available audio and converts it to WAV using FFmpeg.

### 3. Handles local files

If the input is not a URL, it assumes it is a local audio/video file.

`pydub` opens the file and converts it into WAV format.

The audio is converted to:

```text
Mono
16 kHz
WAV
```

### 4. Splits the audio into chunks

The WAV file is divided into **10-minute chunks**.

Each chunk is saved separately.

For example:

```text
audio.wav_chunk_0.wav
audio.wav_chunk_1.wav
audio.wav_chunk_2.wav
```

### 5. Returns the chunks

All generated chunk paths are stored in a list and returned.

## Output:

```python
list
```

The list contains paths to the generated WAV chunks.

Example:

```text
[
    "downloads/video.wav_chunk_0.wav",
    "downloads/video.wav_chunk_1.wav"
]
```

## Connection / Flow:

```text
User's YouTube URL / Local File
↓
audio_processor.py
↓
WAV conversion
↓
10-minute audio chunks
↓
transcriber.py
```

## Why it is needed:

Whisper and Sarvam need audio that can be processed by the transcription system.

This file standardizes different input types into manageable WAV chunks before transcription.

---

# 4. `core/transcriber.py`

## Purpose:

This file converts the audio chunks into text.

It supports two transcription paths:

* **English → local Whisper**
* **Hinglish → Sarvam AI**

It also performs lightweight cleanup of the final transcript.

## Input:

It receives the audio chunks produced by:

```text
audio_processor.py
```

The main function is:

```python
transcribe_all(chunks, language)
```

## What it does:

### 1. Loads the Whisper model when required

`load_model()` loads the configured Whisper model only once.

The model is stored in `_model`.

This prevents the model from being loaded again for every individual chunk.

### 2. Selects the transcription engine

The language determines the route:

```text
English
↓
Whisper
```

or:

```text
Hinglish
↓
Sarvam AI
```

### 3. Transcribes English using Whisper

For English:

```python
transcribe_chunk_whisper()
```

passes the audio chunk to the locally loaded Whisper model.

Whisper returns the recognized English text.

### 4. Processes Hinglish using Sarvam

Sarvam's synchronous API accepts audio of no more than 30 seconds.

Therefore, a 10-minute chunk is further divided into **25-second pieces**.

The flow becomes:

```text
10-minute chunk
↓
25-second pieces
↓
Sarvam API
↓
English translated transcript
↓
Join all pieces
```

The temporary Sarvam pieces are removed after processing.

### 5. Combines and cleans the transcript

`transcribe_all()` processes every audio chunk and combines their text into one large transcript.

`clean_transcript()` then:

* removes immediate repeated words
* removes repeated short phrases
* removes selected filler words
* normalizes whitespace

## Output:

A single cleaned transcript string.

```text
Complete audio/video
↓
Complete text transcript
```

## Connection / Flow:

```text
audio_processor.py
↓
WAV audio chunks
↓
transcriber.py
↓
Whisper / Sarvam
↓
Cleaned complete transcript
↓
summarizer.py
↓
extractor.py
↓
vector_store.py / rag_engine.py
```

## Why it is needed:

The rest of InsightMedia works with text rather than raw audio.

This file is therefore the bridge between the **audio processing stage** and the **AI processing stage**.

---

# 5. `core/summarizer.py`

## Purpose:

This file uses the Groq LLM to generate a title and summary from the transcript.

## Input:

It receives:

```text
Complete transcript
```

from `transcriber.py`.

## What it does:

### 1. Creates the Groq LLM

`get_llm()` creates a `ChatGroq` instance using:

```text
openai/gpt-oss-20b
```

The Groq API key is read from the environment.

### 2. Splits long transcripts

`split_transcript()` uses `RecursiveCharacterTextSplitter`.

It creates chunks of approximately:

```text
3000 characters
```

with:

```text
200 character overlap
```

This allows long transcripts to be processed in smaller sections.

### 3. Generates a title

`generate_title()` sends the beginning of the transcript to the LLM.

The prompt instructs the model to create a short title of no more than 8 words using only information from the transcript.

### 4. Summarizes each transcript chunk

`summarize_chunk()` sends each chunk to the Groq LLM.

The model generates:

```text
2–4 concise bullet points
```

for each chunk.

### 5. Combines the summaries

`summarize()` collects the summaries from all chunks, removes empty and duplicate points, limits the final result to 8 points, and returns the final bullet-point summary.

## Output:

Two main outputs:

```text
Title
+
Summary
```

Example structure:

```text
Title:
Project Planning Discussion

Summary:
- ...
- ...
- ...
```

## Connection / Flow:

```text
transcriber.py
↓
Complete transcript
↓
summarizer.py
↓
Groq LLM
↓
Title + Summary
↓
main.py
↓
app.py
```

## Why it is needed:

A raw transcript can be long and difficult to read.

This file converts the transcript into a short, understandable overview.

---

# 6. `core/extractor.py`

## Purpose:

This file extracts structured information from the transcript.

It identifies:

* Action Items
* Key Decisions
* Open Questions

It also determines whether the content is actually a meeting or not.

## Input:

```text
Complete transcript
```

from `transcriber.py`.

## What it does:

### 1. Classifies the content

`classify_content_type()` asks the Groq LLM to classify the transcript as:

```text
MEETING
```

or:

```text
NOT_MEETING
```

A meeting can contain discussion, tasks, decisions, or follow-up matters.

A lecture, tutorial, documentary, news video, or similar content is classified as `NOT_MEETING`.

### 2. Splits the transcript

For extraction, the transcript is split into chunks of:

```text
2200 characters
```

with:

```text
150 character overlap
```

### 3. Extracts information from each chunk

`extract_from_chunk()` asks the LLM to return JSON containing:

```text
action_items
key_decisions
open_questions
```

The prompt strictly tells the model to use only information explicitly present in the transcript.

### 4. Combines results

`extract_all()` processes every chunk and combines all extracted items.

Duplicate items are removed.

### 5. Formats the final information

The extracted information is converted into user-readable text.

Action items can include:

```text
Task
Owner
Deadline
```

when those details are explicitly available.

Open questions are also filtered so that only actual questions containing `?` are displayed.

## Output:

A dictionary containing:

```python
{
    "action_items": "...",
    "key_decisions": "...",
    "open_questions": "..."
}
```

For non-meeting content, it returns messages such as:

```text
No action items needed.
No key decisions found.
No open questions found.
```

## Connection / Flow:

```text
transcriber.py
↓
Complete transcript
↓
extractor.py
↓
Meeting classification
↓
Chunk-by-chunk extraction
↓
Action Items + Key Decisions + Open Questions
↓
main.py
↓
app.py
```

## Why it is needed:

The summary gives a general overview, but this file extracts specific pieces of useful information from the discussion.

It turns unstructured transcript text into structured meeting insights.

---

# 7. `core/vector_store.py`

## Purpose:

This file converts the transcript into embeddings and stores those embeddings in a local Chroma vector database.

This creates the searchable knowledge base required by the RAG system.

## Input:

```text
Complete transcript
```

## What it does:

### 1. Creates embeddings

The file uses:

```text
all-MiniLM-L6-v2
```

through `HuggingFaceEmbeddings`.

The embedding model runs on CPU.

### 2. Creates a unique collection name

The transcript is passed through an MD5 hash.

A shortened hash is used to create a collection name such as:

```text
meeting_xxxxxxxxxxxx
```

This allows different transcripts to have different Chroma collections.

### 3. Splits the transcript

The transcript is divided into smaller chunks using:

```text
chunk_size = 500
chunk_overlap = 50
```

### 4. Converts chunks into Documents

Each text chunk is wrapped inside a LangChain `Document`.

Metadata is also attached:

```text
chunk_index
```

### 5. Creates and stores the vector database

The documents are converted into embeddings and stored in Chroma.

The persistence directory is:

```text
vectore_db
```

The vector store can later be loaded and searched.

## Output:

A Chroma vector store containing the transcript's embeddings.

It also provides a retriever that can return the most similar chunks.

## Connection / Flow:

```text
transcriber.py
↓
Complete transcript
↓
vector_store.py
↓
Text chunks
↓
Embeddings
↓
Chroma Vector Store
↓
Retriever
↓
rag_engine.py
```

## Why it is needed:

A normal LLM does not automatically know the complete transcript during every question.

The vector store allows the system to find the transcript sections most relevant to a user's question.

---

# 8. `core/rag_engine.py`

## Purpose:

This file creates the RAG question-answering system.

It connects:

```text
Vector Store
+
Retriever
+
Prompt
+
Groq LLM
```

to answer questions using the processed transcript.

## Input:

It receives:

```text
Complete transcript
```

when building the RAG chain.

Later, it receives:

```text
User question
```

when answering questions.

## What it does:

### 1. Builds the vector store

`build_rag_chain()` calls:

```python
build_vector_store(transcript)
```

from `vector_store.py`.

### 2. Creates a retriever

The retriever is configured to retrieve the top:

```text
10
```

similar transcript chunks.

### 3. Formats retrieved documents

`format_docs()` takes the retrieved documents and combines their `page_content` into one context string.

### 4. Builds the RAG chain

The chain follows this structure:

```text
User Question
        +
Relevant Transcript Context
        ↓
Prompt
        ↓
Groq LLM
        ↓
String Output
```

The prompt specifically instructs the LLM to answer only using the meeting transcript context.

It also contains rules for distinguishing between:

```text
Proposal
vs
Actual Decision
```

### 5. Answers questions

`ask_question()` invokes the RAG chain with the user's question.

It also handles Groq rate-limit errors.

## Output:

The main output is an answer to the user's question.

Example:

```text
User:
What decision was made about the project?

Assistant:
The group agreed to...
```

The answer is based on retrieved transcript context.

## Connection / Flow:

```text
vector_store.py
↓
Chroma Vector Store
↓
Retriever
↓
Relevant transcript chunks
↓
rag_engine.py
↓
Groq LLM
↓
Answer
↓
main.py / app.py
↓
User
```

## Why it is needed:

This is what allows InsightMedia to behave like a **chat interface for the processed video or meeting**.

Instead of sending the entire transcript blindly for every question, the retriever first finds relevant transcript sections and provides them to the LLM as context.

---

# 9. `main.py`

## Purpose:

`main.py` is the central pipeline coordinator.

It connects the individual processing modules together.

It does not perform all processing itself. Instead, it calls the appropriate functions from the other files in the correct order.

## Input:

```text
YouTube URL
OR
Local audio/video file path

+
Language
```

The language can be:

```text
english
```

or:

```text
hinglish
```

## What it does:

### 1. Processes the input

Calls:

```python
process_input(source)
```

from `audio_processor.py`.

This produces audio chunks.

### 2. Creates the transcript

Calls:

```python
transcribe_all(chunks, language)
```

from `transcriber.py`.

This produces the complete transcript.

### 3. Generates AI insights

It calls:

```python
generate_title(transcript)
summarize(transcript)
extract_information(transcript)
```

These produce:

```text
Title
Summary
Action Items
Key Decisions
Open Questions
```

### 4. Builds the RAG system

It calls:

```python
build_rag_chain(transcript)
```

This creates the searchable RAG chain.

### 5. Returns everything together

`run_pipeline()` returns a dictionary containing:

```python
{
    "title": ...,
    "transcript": ...,
    "summary": ...,
    "action_items": ...,
    "key_decisions": ...,
    "open_questions": ...,
    "rag_chain": ...
}
```

## Output:

A complete result dictionary containing both the generated insights and the RAG chain.

## Connection / Flow:

```text
User Input
↓
main.py
↓
audio_processor.py
↓
Audio Chunks
↓
transcriber.py
↓
Transcript
↓
summarizer.py
↓
Title + Summary
↓
extractor.py
↓
Action Items + Decisions + Questions
↓
vector_store.py
↓
Chroma Vector Store
↓
rag_engine.py
↓
RAG Chain
↓
Complete Result Dictionary
```

## Why it is needed:

Without `main.py`, the individual modules would exist separately without one central pipeline connecting them.

It acts as the **orchestrator of the backend processing flow**.

It also provides a CLI entry point where the user can directly enter a URL/file and chat with the processed content.

---

# 10. `app.py`

## Purpose:

`app.py` is the Streamlit frontend of InsightMedia.

It provides the user interface through which the user can:

* select the type of input
* provide a YouTube URL
* upload a local file
* select English or Hinglish
* start analysis
* view generated results
* view the transcript
* ask RAG questions

## Input:

The UI accepts:

```text
YouTube URL
OR
Uploaded local audio/video file
```

It also accepts:

```text
Language selection
```

and:

```text
RAG questions
```

## What it does:

### 1. Sets up the Streamlit application

It configures:

* Page title
* Page icon
* Wide layout
* Custom CSS

### 2. Provides navigation

The sidebar contains:

```text
Home
New Analysis
Chat (RAG)
```

It also displays the application's feature list.

### 3. Collects the user's input

For YouTube:

```text
YouTube URL → text input
```

For local files:

```text
Upload → temporary file → file path
```

The user can also select:

```text
English
Hinglish
```

### 4. Starts the backend pipeline

When the user clicks:

```text
Analyze Video
```

the app calls:

```python
run_pipeline(source, language)
```

from `main.py`.

The returned result is stored in:

```python
st.session_state.result
```

### 5. Displays the results

The app displays:

```text
Title
Summary
Action Items
Key Decisions
Open Questions
Full Transcript
```

### 6. Provides RAG chat

When the user opens:

```text
Chat (RAG)
```

the app gets the RAG chain from:

```python
st.session_state.result["rag_chain"]
```

The user enters a question.

The question is passed to:

```python
ask_question(rag_chain, question)
```

The answer is displayed in the chat interface and stored in `st.session_state.messages`.

## Output:

The final output is the **InsightMedia web interface** containing:

```text
AI-generated title
AI summary
Action items
Key decisions
Open questions
Full transcript
RAG Q&A
```

## Connection / Flow:

```text
User
↓
Streamlit app.py
↓
run_pipeline()
↓
main.py
↓
Processing + AI + RAG
↓
Result Dictionary
↓
app.py
↓
Results displayed to User
↓
User asks RAG question
↓
rag_engine.py
↓
Answer
↓
Streamlit Chat
```

## Why it is needed:

`app.py` turns the backend pipeline into a usable application.

Instead of running Python functions manually, the user can interact with InsightMedia through a visual interface.

---

# Complete Project Flow

The complete project can be represented as:

```text
                    USER
                      │
                      ▼
             YouTube URL / Local File
                      │
                      ▼
              ┌─────────────────┐
              │     app.py      │
              │   Streamlit UI  │
              └────────┬────────┘
                       │
                       ▼
                  main.py
              Pipeline Controller
                       │
                       ▼
            audio_processor.py
                       │
              Audio Processing
                       │
                       ▼
                 WAV Chunks
                       │
                       ▼
              transcriber.py
                       │
              ┌────────┴────────┐
              │                 │
           English           Hinglish
              │                 │
              ▼                 ▼
           Whisper           Sarvam AI
              │                 │
              └────────┬────────┘
                       │
                       ▼
              Complete Transcript
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
    summarizer.py  extractor.py  vector_store.py
          │            │            │
          ▼            ▼            ▼
       Title +      Actions +    Embeddings
       Summary      Decisions +       │
                     Questions         ▼
                                  ChromaDB
                                      │
                                      ▼
                                 Retriever
                                      │
                                      ▼
                               rag_engine.py
                                      │
                                      ▼
                                   Groq LLM
                                      │
                                      ▼
                                 RAG Answer
                                      │
                                      ▼
                                  app.py
                                      │
                                      ▼
                                    USER
```

---

# Detailed End-to-End Flow

## Step 1 — User provides input

The user starts from the Streamlit interface.

They provide either:

```text
YouTube URL
```

or:

```text
Local audio/video file
```

They also select:

```text
English
```

or:

```text
Hinglish
```

---

## Step 2 — `app.py` sends the input to `main.py`

When the user clicks **Analyze Video**, `app.py` calls:

```python
run_pipeline(source, language)
```

This transfers control to the backend pipeline.

---

## Step 3 — `main.py` calls `audio_processor.py`

`main.py` calls:

```python
process_input(source)
```

The input is checked.

If it is a URL:

```text
YouTube URL
↓
yt-dlp
↓
Audio
↓
WAV
```

If it is a local file:

```text
Local File
↓
pydub
↓
WAV
```

The WAV audio is standardized to mono and 16 kHz for local-file conversion.

---

## Step 4 — Audio is divided into chunks

The processed WAV file is divided into 10-minute chunks.

For a longer recording:

```text
Full Audio
↓
Chunk 1
Chunk 2
Chunk 3
...
```

These chunk paths are returned to `main.py`.

---

## Step 5 — `main.py` sends chunks to `transcriber.py`

`transcribe_all()` processes each audio chunk.

The selected language determines the transcription path.

### English:

```text
Audio Chunk
↓
Local Whisper
↓
English Text
```

### Hinglish:

```text
10-minute Audio Chunk
↓
25-second pieces
↓
Sarvam API
↓
English translated text
```

All text is combined into one complete transcript.

---

## Step 6 — Transcript cleanup

The transcript is cleaned by `clean_transcript()`.

It removes certain immediate repetitions and filler expressions and normalizes whitespace.

The result is:

```text
Complete Clean Transcript
```

---

## Step 7 — Title generation

`main.py` passes the transcript to:

```python
generate_title()
```

in `summarizer.py`.

The Groq LLM generates a short title based only on the transcript.

Output:

```text
Title
```

---

## Step 8 — Summary generation

The transcript is split into smaller sections.

Each section is summarized by the Groq LLM.

The individual summaries are combined.

Duplicate points are removed and the final result is limited to 8 points.

Output:

```text
Summary
```

---

## Step 9 — Information extraction

The transcript is passed to:

```python
extract_information()
```

in `extractor.py`.

First, the LLM determines whether the content is:

```text
MEETING
```

or:

```text
NOT_MEETING
```

If it is a meeting, the transcript is processed in chunks.

The LLM extracts:

```text
Action Items
Key Decisions
Open Questions
```

The results are combined, duplicates are removed, and the information is formatted for display.

---

## Step 10 — Vector store creation

The transcript is passed to:

```python
build_rag_chain()
```

in `rag_engine.py`.

That function calls:

```python
build_vector_store()
```

from `vector_store.py`.

The transcript is split into smaller chunks.

Each chunk becomes a LangChain `Document`.

Then:

```text
Text Chunk
↓
Embedding Model
↓
Vector
↓
ChromaDB
```

The vectors are stored locally in:

```text
vectore_db
```

---

## Step 11 — Retriever creation

The vector store creates a retriever.

The retriever can search the stored transcript embeddings and return the most relevant transcript sections.

In the RAG chain, the configured retriever returns the top 10 similar chunks.

---

## Step 12 — RAG chain creation

The RAG chain connects:

```text
Question
+
Retrieved Transcript Context
↓
Prompt
↓
Groq LLM
↓
Answer
```

The prompt instructs the LLM to use only the transcript context.

---

## Step 13 — `main.py` returns the complete result

The pipeline returns:

```text
Title
Transcript
Summary
Action Items
Key Decisions
Open Questions
RAG Chain
```

as one dictionary.

---

## Step 14 — `app.py` displays the results

The Streamlit application reads the result dictionary and displays the information in separate sections.

The user can see:

```text
📌 Title
📋 Summary
✅ Action Items
🔑 Key Decisions
❓ Open Questions
📄 Full Transcript
```

---

## Step 15 — User asks a question

The user goes to:

```text
Chat (RAG)
```

and enters a question.

For example:

```text
What did they decide about the project?
```

---

## Step 16 — RAG retrieves relevant information

The question goes to the retriever.

The retriever searches the Chroma vector store and finds transcript chunks that are semantically related to the question.

Those chunks become the context for the LLM.

---

## Step 17 — Groq generates the answer

The relevant transcript context and user's question are sent through the RAG prompt to the Groq LLM.

The LLM generates the answer using the provided transcript context.

---

## Step 18 — Answer returns to Streamlit

The answer is returned through:

```text
rag_engine.py
↓
app.py
↓
Streamlit Chat
```

The answer is displayed to the user.

The conversation messages are stored in Streamlit session state so they remain visible during the current app session.

---

# One-Line Summary

| File                 | One-Line Purpose                                                                      |
| -------------------- | ------------------------------------------------------------------------------------- |
| `.env`               | Stores API keys and configuration values used by the application.                     |
| `requirements.txt`   | Lists the Python dependencies required to run InsightMedia.                           |
| `audio_processor.py` | Converts YouTube/local media into standardized WAV audio chunks.                      |
| `transcriber.py`     | Converts audio chunks into a cleaned text transcript using Whisper or Sarvam.         |
| `summarizer.py`      | Uses the Groq LLM to generate a title and concise summary from the transcript.        |
| `extractor.py`       | Uses the Groq LLM to identify action items, decisions, and open questions.            |
| `vector_store.py`    | Converts transcript chunks into embeddings and stores them in ChromaDB for retrieval. |
| `rag_engine.py`      | Combines retrieval and the Groq LLM to answer questions using transcript context.     |
| `main.py`            | Connects all backend modules into one complete processing pipeline.                   |
| `app.py`             | Provides the Streamlit interface for analysis, displaying results, and RAG chat.      |

---

# Final Project Summary

InsightMedia takes a **YouTube video or local audio/video file** and converts it into useful AI-generated information.

The process starts in the Streamlit interface:

```text
User
↓
YouTube URL / Local File
```

`main.py` coordinates the backend processing.

First, `audio_processor.py` prepares the media by converting it to WAV and splitting it into manageable audio chunks.

Then `transcriber.py` converts those chunks into text. English content is processed using the local Whisper model, while Hinglish content is processed through Sarvam's speech-to-text translation API.

The resulting transcript is sent to two different AI-processing paths.

`summarizer.py` uses the Groq LLM to generate a title and summary.

`extractor.py` uses the Groq LLM to determine whether the content is a meeting and, when appropriate, extracts action items, key decisions, and open questions.

At the same time, the transcript is passed into `vector_store.py`. The transcript is split into smaller pieces, converted into embeddings using the HuggingFace embedding model, and stored locally in ChromaDB.

`rag_engine.py` uses this vector database to retrieve transcript sections relevant to a user's question. Those retrieved sections are provided to the Groq LLM as context, allowing the system to answer questions based on the processed video.

Finally, `app.py` presents everything through the Streamlit interface.

The overall concept is:

```text
User Input
    ↓
Audio / Video Processing
    ↓
Audio Chunks
    ↓
Speech-to-Text
    ↓
Complete Transcript
    ↓
 ┌───────────────┬────────────────┬─────────────────┐
 ↓               ↓                ↓
Summary       Information      Vector Store
Generation    Extraction       + Embeddings
 ↓               ↓                ↓
Title +       Actions +       ChromaDB
Summary       Decisions +         ↓
              Questions       Retriever
                                  ↓
                              RAG Engine
                                  ↓
                              Groq LLM
                                  ↓
                              Q&A Answer
 └───────────────┴────────────────┴─────────────────┘
                         ↓
                     Streamlit
                         ↓
                        User
```

In simple terms, **InsightMedia takes a video or audio recording, understands what was said, turns it into a transcript, extracts useful insights from it, and then creates a searchable AI-powered interface where the user can ask questions about that content.**

**One security note:** because the API credentials were pasted here, treat them as exposed and rotate them before using this project publicly or pushing the `.env` file to GitHub.
