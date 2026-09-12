import os
import shutil
import tempfile
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import functions from cataloger modules
from extractor import extract_product_data
from question_generator import generate_artisan_questions
from speech_to_text import transcribe_audio
from translator import translate_text
from validator import validate_artisan_answer

app = FastAPI(title="Artisan AI Microservice API", version="1.0")

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Request Schemas
# ==========================================

class QuestionGenRequest(BaseModel):
    llm_visual_analysis: Dict[str, Any]
    user_description: Optional[str] = ""

class ValidateAnswerRequest(BaseModel):
    question_text: str
    question_type: str
    transcribed_answer: str

class TranslationRequest(BaseModel):
    text: str
    target_language: str = "en"


# ==========================================
# API Endpoints
# ==========================================

@app.get("/")
def read_root():
    return {"status": "online", "message": "Artisan AI FastAPI Server Running"}


@app.post("/api/extract-visuals")
async def api_extract_visuals(image: UploadFile = File(...)):
    """Endpoint to process uploaded product image through vision LLM."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as temp_img:
            shutil.copyfileobj(image.file, temp_img)
            temp_path = temp_img.name

        # Process image using extract_product_data from extractor.py
        extracted_data = extract_product_data(temp_path)
        os.remove(temp_path)
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-questions")
def api_generate_questions(data: QuestionGenRequest):
    """Endpoint to generate deduplicated artisan questions."""
    try:
        result = generate_artisan_questions(
            llm_visual_analysis=data.llm_visual_analysis,
            user_description=data.user_description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transcribe-audio")
async def api_transcribe_audio(
    audio: UploadFile = File(...), 
    language: Optional[str] = Form(None), 
    prompt: Optional[str] = Form(None)
):
    """Endpoint to transcribe voice audio files using Groq Whisper."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as temp_audio:
            shutil.copyfileobj(audio.file, temp_audio)
            temp_path = temp_audio.name

        transcription = transcribe_audio(temp_path, language=language, prompt=prompt)
        os.remove(temp_path)
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate-answer")
def api_validate_answer(data: ValidateAnswerRequest):
    """Endpoint to validate transcribed user answer against the asked question."""
    try:
        result = validate_artisan_answer(
            question_text=data.question_text,
            question_type=data.question_type,
            transcribed_answer=data.transcribed_answer
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/translate")
def api_translate(data: TranslationRequest):
    """Endpoint to handle language translation."""
    try:
        translated_text = translate_text(data.text, target_language=data.target_language)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)