import os
import json
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini Client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in your environment!")

client = genai.Client(api_key=api_key)


# Pydantic Schema mapping directly to your ML model's expected features
class MLFeatureSchema(BaseModel):
    product_category: str = Field(
        description="Broader product category matching dataset categories (e.g., 'Pottery & Terracotta', 'Handloom & Textiles', 'Woodwork')."
    )
    product_type: str = Field(
        description="Specific product type (e.g., 'Decorative pot', 'Saree', 'Wall hanging')."
    )
    material_cost: float = Field(
        description="Numerical cost of raw materials in INR. Must be > 0."
    )
    production_time_days: float = Field(
        description="Total production duration in days (can be fractional, e.g., 0.5 for 12 hours). Must be > 0."
    )
    region: str = Field(
        description="Geographic region in India (e.g., 'South', 'North', 'East', 'West', 'Central')."
    )
    origin_state: str = Field(
        description="Indian state of origin (e.g., 'Telangana', 'Andhra Pradesh', 'Rajasthan', 'West Bengal')."
    )
    demand_index: float = Field(
        description="Float index strictly between 0.0 and 1.0 reflecting market demand."
    )
    market_trend: float = Field(
        description="Float market trend multiplier/index (e.g., 0.5 to 2.0)."
    )
    material_type: str = Field(
        description="Primary material name (e.g., 'Terracotta Clay', 'Cotton', 'Teak Wood', 'Silk')."
    )


def extract_ml_features(
    llm_visual_analysis: Dict[str, Any],
    user_description: str = "",
    qa_responses: Optional[List[Dict[str, Any]]] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Extracts and standardizes raw inputs into structured features for the ML model.
    """
    qa_responses = qa_responses or []

    qa_formatted_text = ""
    if qa_responses:
        for idx, item in enumerate(qa_responses, start=1):
            q_text = item.get("question_text", item.get("question_id", ""))
            ans_text = item.get("answer", "")
            qa_formatted_text += f"  {idx}. Q: {q_text} | A: {ans_text}\n"
    else:
        qa_formatted_text = "  No direct follow-up Q&A responses provided."

    major_category = llm_visual_analysis.get("major_category", "Handicraft")
    sub_category = llm_visual_analysis.get("sub_category", "General Item")
    materials = llm_visual_analysis.get("materials_detected", [])
    features = llm_visual_analysis.get("visual_features", [])

    prompt = f"""
    You are an AI Feature Extraction Agent for an Indian Artisan E-commerce platform.
    Extract the exact structured numerical and categorical features required by an ML pricing model.

    --- SOURCE DATA ---
    1. VISUAL EXTRACTION DETAILS:
       - Major Category: {major_category}
       - Sub Category: {sub_category}
       - Visually Detected Materials: {', '.join(materials) if materials else 'None'}
       - Visual Features: {', '.join(features) if features else 'None'}

    2. USER INITIAL DESCRIPTION:
       "{user_description if user_description.strip() else 'No initial text provided.'}"

    3. ARTISAN CONFIRMED ANSWERS:
{qa_formatted_text}

    --- EXTRACTION RULES ---
    1. Extract numerical values for `material_cost` and `production_time_days` from confirmed Q&A or descriptions.
       - If material cost is not explicitly mentioned, estimate a realistic INR cost based on raw materials and item complexity.
       - If production time is given in hours, convert it to fractional days (e.g., 12 hours = 0.5). Default to 1.0 day if unknown.
    2. Set `demand_index` (0.0 to 1.0) and `market_trend` (0.5 to 2.0) based on craft complexity and popularity.
    3. Standardize text fields (`product_category`, `product_type`, `material_type`, `region`, `origin_state`) to clean string values without extra spaces.
    """

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MLFeatureSchema,
                    temperature=0.1
                )
            )
            return json.loads(response.text)

        except (ServerError, APIError) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"[!] API error encountered, retrying ({attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e


if __name__ == "__main__":
    sample_visual = {
        "major_category": "Pottery & Terracotta",
        "sub_category": "Decorative pot",
        "materials_detected": ["Terracotta Clay", "Natural Pigments"],
        "visual_features": ["Hand-painted floral patterns"]
    }

    sample_user_text = "Handcrafted clay pot made using organic red clay from Warangal."

    sample_qa = [
        {"question_text": "What is the cost of raw materials used?", "answer": "150 rupees for clay and paints"},
        {"question_text": "How long did it take to complete this item?", "answer": "It took 3 days to shape, dry, and paint"},
        {"question_text": "Which state and region is this craft from?", "answer": "Telangana, South India"}
    ]

    print("[+] Extracting features for ML model input...")
    extracted_features = extract_ml_features(sample_visual, sample_user_text, sample_qa)
    
    print("\n--- EXTRACTED ML FEATURES ---")
    print(json.dumps(extracted_features, indent=2))