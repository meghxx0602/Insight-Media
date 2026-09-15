import whisper
import os
import requests
from pydub import AudioSegment

import re

def clean_transcript(text: str) -> str:
    """
    Lightweight, rule-based cleanup — no LLM call, no rewriting of meaning.
    - Collapses immediate repeated words/phrases (common Whisper artifact).
    - Removes a small set of filler words.
    - Normalizes whitespace.
    """
    # Collapse immediate repeated single words: "the the" -> "the"
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)

    # Collapse immediate repeated short phrases (2-4 words): "you know you know" -> "you know"
    text = re.sub(r'\b((?:\w+\s+){1,3}\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)

    # Remove common filler words/phrases (safe, meaning-preserving)
    fillers = [
        r'\bum+\b', r'\buh+\b', r'\byou know\b',
        r'\bi mean\b', r'\bsort of\b', r'\bkind of\b'
    ]
    for filler in fillers:
        text = re.sub(filler, '', text, flags=re.IGNORECASE)

    # Normalize whitespace left behind
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Sarvam's sync STT-translate API rejects audio longer than 30s.
# We slice each chunk into 25s pieces (with a 5s safety margin) before sending.
SARVAM_PIECE_SECONDS = 25


WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small") #Small, using this locally


SARVAM_API_KEY = os.getenv("SARVAM_API_KEY") #Creating end point to integrate sarvam
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

_model = None


def load_model(): #Whisper ka small model load karta hai,
    #Har baar transcription ke liye model dobara load na ho, Ek baar load karke _model mein rakh deta hai.

    global _model  

    if _model is None: #Locally storing the model
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL) 
        print("Whisper model loaded.")
    return _model #Model used for transcription, model in memory


def transcribe_chunk_whisper(chunk_path: str) -> str: #Ye English audio chunk → English text karta hai, single audio chunk

    model = load_model()  

    result = model.transcribe(chunk_path, task="transcribe")  
    return result["text"]  #One audio chunk → English transcript

# Sarvam API Call - Audio ka ek small piece Sarvam ko bhejna → Sarvam se English translated transcript lena.
# Sarvam ke saath communication handle karta hai.
def _send_to_sarvam(piece_path: str) -> str:
    """Send one ≤30s WAV file to Sarvam and return the English transcript."""
    headers = {"api-subscription-key": SARVAM_API_KEY}

    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\n❌ Sarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    #10-minute Hinglish audio → 25-sec pieces → Sarvam → English transcript
    """
    Sarvam sync API only accepts ≤30s audio. We split this chunk into
    25-second pieces, send each separately, and join the transcripts.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            print(f"  → Sarvam piece {i + 1}/{total_pieces} ...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()

   



def transcribe_chunk(chunk_path: str, language: str = "english") -> str: 
    """
    Iska kaam khud transcription karna nahi hai, decides ki whisper use kru ya sarvam, if lang = english then whisper or sarvam if hinglish
    Route one chunk to Whisper or Sarvam depending on language choice.
    - english  → Whisper (local model)
    - hinglish → Sarvam (translates to English while transcribing)
    """
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path) #Us chunk ka transcript.
    return transcribe_chunk_whisper(chunk_path) #Us chunk ka transcript.


def transcribe_all(chunks: list, language: str = "english") -> str: 
    """
    For long video (above 10 mins) more chunks hence a func in order translate/transcribe the other chunks, 
    this func uses the transcribe_chunk func to transcribe single chunks, thus if one chunk has error it stops and error caught, if wrapped in a single func then error nai pata chlta
    Ye main function hai jo poore video ke transcript ko banata hai.
    transcribe_all() ek-ek karke sare chunks ko process karta hai.
    """
    full_transcript = "" 

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"
    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):  #Idhar loop mai pehle func ko use krte and uska output full transcrip mai we save 

        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(chunk, language=language)  

        full_transcript += text + " "  

    print("Transcription complete.")

    return clean_transcript(full_transcript.strip())  #One big string containing the complete transcript.