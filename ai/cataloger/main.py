import os
import sys
import shutil
import tempfile
from typing import Dict, Any, Optional, List
import cv2
import numpy as np

# ==========================================
# PRICING IMPORTS
# ==========================================
import pandas as pd
import joblib

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ==========================================
# PATH ROUTING (Allows access to sibling folders without breaking cataloger)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# ==========================================
# CATALOGER IMPORTS (Strictly Unchanged)
# ==========================================
from extractor import extract_product_data
from question_generator import generate_artisan_questions
from speech_to_text import transcribe_audio
from translator import translate_text
from validator import validate_artisan_answer
from final_description import generate_final_product_description

# ==========================================
# SIBLING IMPORTS (Image Enhancer & Pricing)
# ==========================================
from image_enhancer.blurr_tester import validate_image_sharpness
from image_enhancer.image_enhancer import process_lighting_pipeline
from image_enhancer.background_remover import remove_product_background
from image_enhancer.formatter import format_ecommerce_canvas


app = FastAPI(
    title="Artisan AI Microservice API",
    version="1.0"
)

# ==========================================
# LOAD MACHINE LEARNING MODEL
# ==========================================
# Loads once when the server starts to keep API responses lightning fast
try:
    pricing_model = joblib.load("catboost_pricing_model.pkl")
    print("CatBoost Pricing Model loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load pricing model. Ensure 'catboost_pricing_model.pkl' is in the same directory. Error: {e}")
    pricing_model = None


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

class PricingRequest(BaseModel):
    product_category: str
    product_type: str
    material_cost: float
    production_time_days: int
    region: str
    origin_state: str
    demand_index: float
    market_trend: float
    material_type: str


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
# 7. IMAGE ENHANCEMENT PIPELINE
# ==========================================

@app.post("/api/process-product-image")
async def api_process_product_image(image: UploadFile = File(...)):
    """
    Unified image pipeline endpoint that connects:
    1. Blur Validation
    2. Zero-DCE Lighting Enhancement
    3. Background Removal (rembg)
    4. 1080x1080 White Canvas & Drop Shadow Formatting
    """
    try:
        raw_bytes = await image.read()
        image_matrix = cv2.imdecode(np.frombuffer(raw_bytes, np.uint8), cv2.IMREAD_COLOR)

        if image_matrix is None:
            raise HTTPException(status_code=400, detail="Invalid image file provided.")

        is_sharp, score, blur_msg = validate_image_sharpness(image_matrix)
        if not is_sharp:
            return {"status": "rejected", "step": "blur_check", "message": blur_msg, "score": score}

        success_light, enhanced_matrix, light_msg = process_lighting_pipeline(image_matrix)
        if not success_light:
            raise HTTPException(status_code=500, detail=light_msg)

        success_bg, rgba_matrix, bg_msg = remove_product_background(enhanced_matrix)
        if not success_bg:
            raise HTTPException(status_code=500, detail=bg_msg)

        success_canvas, final_canvas, canvas_msg = format_ecommerce_canvas(rgba_matrix, canvas_size=1080, padding=120)
        if not success_canvas:
            raise HTTPException(status_code=500, detail=canvas_msg)

        output_dir = "processed_outputs"
        os.makedirs(output_dir, exist_ok=True)
        safe_filename = f"product_{os.path.splitext(image.filename)[0]}.jpg"
        output_path = os.path.join(output_dir, safe_filename)
        
        cv2.imwrite(output_path, final_canvas)

        return {
            "status": "success",
            "message": "Image processing pipeline executed successfully.",
            "saved_file_path": output_path,
            "blur_score": score
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 8. PREDICT PRODUCT SELLING PRICE
# ==========================================

@app.post("/api/predict-price")
async def get_price_prediction(data: PricingRequest):
    """Endpoint to predict fair market value using CatBoost model."""
    if pricing_model is None:
        raise HTTPException(status_code=500, detail="Pricing model is not loaded on the server.")

    try:
        # Convert incoming JSON data into a DataFrame format
        input_data = pd.DataFrame([data.model_dump()])
        
        # Make the prediction
        predicted_price = pricing_model.predict(input_data)[0]
        
        return {
            "status": "success",
            "predicted_price": round(float(predicted_price), 2),
            "currency": "INR"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


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