# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ========== OPENAI ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
REALTIME_MODEL = os.getenv("REALTIME_MODEL", "gpt-4o-realtime-preview")

OPENAI_MODEL_TEXT = os.getenv("OPENAI_MODEL_TEXT", "gpt-4.1-mini")   # ou gpt-4o-mini
OPENAI_MODEL_STT  = os.getenv("OPENAI_MODEL_STT",  "whisper-1")
OPENAI_MODEL_TTS  = os.getenv("OPENAI_MODEL_TTS",  "tts-1")
OPENAI_TTS_VOICE  = os.getenv("OPENAI_TTS_VOICE",  "alloy")


# ========== GOOGLE AUTH ==========
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

# ========== JWT INTERNO DO AIA ==========
AIA_JWT_SECRET = os.getenv("AIA_JWT_SECRET", "change-me")
AIA_JWT_ALGORITHM = os.getenv("AIA_JWT_ALGORITHM", "HS256")
AIA_JWT_EXP_HOURS = int(os.getenv("AIA_JWT_EXP_HOURS", "8"))

# ========== POSTGRES ==========
POSTGRES_URL = os.getenv("POSTGRES_URL", "")

# ========== OUTROS (OPCIONAIS) ==========
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
