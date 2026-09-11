import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini Client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in your environment!")

client = genai.Client(api_key=api_key)


# Define Question Schema
class QuestionOption(BaseModel):
    option_id: str = Field(description="Unique short code/key for the option, e.g., 'opt_1', 'pure_pattu', 'silk_cotton'.")
    option_text: str = Field(description="Display label for the user in clear, accessible language.")

class InteractiveQuestion(BaseModel):
    question_id: str = Field(description="Unique snake_case identifier for the attribute, e.g., 'material_type_confirmation', 'dimensions_cm', 'care_instructions'.")
    question_text: str = Field(description="User-friendly question worded respectfully for artisans and micro-entrepreneurs.")
    question_type: str = Field(description="Type of input: 'single_choice', 'multiple_choice', 'text_input', or 'number_input'.")
    options: Optional[List[QuestionOption]] = Field(default=None, description="List of options if single_choice or multiple_choice.")
    is_required: bool = Field(default=True, description="Whether this information is critical for e-commerce listing.")
    explanation_tip: Optional[str] = Field(default=None, description="A simple tip explaining WHY this detail helps buyers.")

class ProductQuestionnaire(BaseModel):
    product_title_suggestion: str = Field(description="Suggested e-commerce title generated from visual analysis.")
    missing_critical_attributes: List[str] = Field(description="Key attributes missing or requiring confirmation (e.g., Exact Material Type, Dimensions, Care instructions).")
    questions: List[InteractiveQuestion] = Field(description="List of 3 to 5 tailored questions to ask the seller.")


def generate_artisan_questions(extracted_visual_data: dict, max_retries: int = 3) -> dict:
    """
    Generates intelligent follow-up questions tailored to the artisan based on the image classification output,
    explicitly verifying materials and weave types while avoiding unverified visual assumptions.
    """
    
    major_category = extracted_visual_data.get("major_category", "General Craft")
    sub_category = extracted_visual_data.get("sub_category", "General")
    materials = extracted_visual_data.get("materials_detected", [])
    features = extracted_visual_data.get("visual_features", [])
    brief_summary = extracted_visual_data.get("brief_summary", "")

    prompt = f"""
    You are an AI assistant helping Indian micro-entrepreneurs, rural artisans, and handloom weavers digitize their products for e-commerce.

    --- VISUAL EXTRACTION ANALYSIS ---
    Major Category: {major_category}
    Sub-Category: {sub_category}
    Materials Detected visually: {', '.join(materials) if materials else 'None identified'}
    Visual Features: {', '.join(features) if features else 'None identified'}
    Visual Summary: {brief_summary}

    --- TASK ---
    Generate 3 to 5 clear, friendly, and practical questions for the seller.
    NEVER assume visual predictions about raw materials or fabric types are 100% accurate. You MUST ask the seller to verify and specify exact material details along with non-visual specifications.

    --- MANDATORY QUESTION RULES ---
    1. **Always Verify Material & Fabric Type**:
       - For Handloom/Sarees/Textiles: Always ask for exact fabric verification (e.g., "Is this Pure Pattu / Mulberry Silk, Silk-Cotton Mix, Art Silk, Dupion, or Pure Cotton?").
       - Ask whether it includes Silk Mark certification or Handloom mark if applicable.
    2. **Collect Critical Non-Visual Specs**:
       - Dimensions: Length/Width in meters or inches, Saree length (e.g., 5.5m vs 6.3m with blouse piece).
       - Care Instructions: Dry clean only, hand wash, or machine wash.
       - Crafting Process: Pure handloom vs powerloom, weaving method (e.g., Kanchipuram, Banarasi, Pochampally, Ikkat).
    3. **User-Friendly Options**:
       - Provide clickable preset options (`single_choice` or `multiple_choice`) so the artisan can quickly select without typing lengthy text.
    4. Provide an optional tip (`explanation_tip`) showing why buyers look for this specification.
    """

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ProductQuestionnaire,
                    temperature=0.2
                )
            )
            return json.loads(response.text)
        
        except (ServerError, APIError) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"[!] API error standard backoff retry ({attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e


if __name__ == "__main__":
    # Example input for a saree
    sample_extracted_data = {
        "is_valid_artisan_product": True,
        "major_category": "3. Pottery & Terracotta",
        "sub_category": "Decorative pots",
        "materials_detected": ["Terracotta", "Clay", "Natural pigment"],
        "visual_features": ["Hand-painted floral motifs", "Earthy red tone", "Narrow neck matte finish"],
        "confidence_score": 0.95,
        "brief_summary": "Handcrafted earthen terracotta pot with traditional floral hand-paintings."
    }

    print("[+] Generating tailored cataloging questions for artisan...")
    questions_data = generate_artisan_questions(sample_extracted_data)
    
    print("\n--- GENERATED QUESTIONNAIRE ---")
    print(json.dumps(questions_data, indent=2))