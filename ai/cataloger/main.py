import os
import shutil
import tempfile
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import functions from cataloger modules
from extractor import extract_product_data
from question_generator import generate_artisan_questions
from speech_to_text import transcribe_audio
from translator import translate_text
from validator import validate_artisan_answer
from final_description import generate_final_product_description


app = FastAPI(
    title="Artisan AI Microservice API",
    version="1.0"
)


# ==========================================
# CORS
# ==========================================

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


class ProductDescriptionRequest(BaseModel):
    llm_visual_analysis: Dict[str, Any]
    user_description: Optional[str] = ""
    qa_responses: Optional[List[Dict[str, Any]]] = None


# ==========================================
# Root Endpoint
# ==========================================

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Artisan AI FastAPI Server Running"
    }


# ==========================================
# 1. EXTRACT VISUALS
# ==========================================

@app.post("/api/extract-visuals")
async def api_extract_visuals(
    image: UploadFile = File(...)
):
    """Endpoint to process uploaded product image through vision LLM."""

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(image.filename)[1]
        ) as temp_img:

            shutil.copyfileobj(image.file, temp_img)
            temp_path = temp_img.name

        extracted_data = extract_product_data(temp_path)

        return extracted_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ==========================================
# 2. GENERATE QUESTIONS
# ==========================================

@app.post("/api/generate-questions")
def api_generate_questions(
    data: QuestionGenRequest
):
    """Endpoint to generate targeted artisan questions."""

    try:
        result = generate_artisan_questions(
            llm_visual_analysis=data.llm_visual_analysis,
            user_description=data.user_description
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# 3. TRANSCRIBE AUDIO
# ==========================================

@app.post("/api/transcribe-audio")
async def api_transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None)
):
    """Endpoint to transcribe voice audio files using Groq Whisper."""

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(audio.filename)[1]
        ) as temp_audio:

            shutil.copyfileobj(audio.file, temp_audio)
            temp_path = temp_audio.name

        transcription = transcribe_audio(
            temp_path,
            language=language,
            prompt=prompt
        )

        return {
            "transcription": transcription
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ==========================================
# 4. VALIDATE ANSWER
# ==========================================

@app.post("/api/validate-answer")
def api_validate_answer(
    data: ValidateAnswerRequest
):
    """Endpoint to validate transcribed user answer."""

    try:
        result = validate_artisan_answer(
            question_text=data.question_text,
            question_type=data.question_type,
            transcribed_answer=data.transcribed_answer
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# 5. TRANSLATE TEXT
# ==========================================

@app.post("/api/translate")
def api_translate(
    data: TranslationRequest
):
    """Endpoint to handle language translation."""

    try:
        translated_text = translate_text(
            data.text,
            target_lang=data.target_language
        )

        return {
            "translated_text": translated_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# 6. GENERATE FINAL PRODUCT DESCRIPTION
# ==========================================

@app.post("/api/generate-description")
def api_generate_description(
    data: ProductDescriptionRequest
):
    """Endpoint to generate final e-commerce product description."""

    try:
        result = generate_final_product_description(
            llm_visual_analysis=data.llm_visual_analysis,
            user_description=data.user_description,
            qa_responses=data.qa_responses
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )