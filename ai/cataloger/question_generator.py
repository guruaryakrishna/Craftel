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


# Pydantic Schemas for Structured Output
class QuestionOption(BaseModel):
    option_id: str = Field(description="Unique short key for the option, e.g., 'confirm_clay', 'kg', 'opt_1'.")
    option_text: str = Field(description="Display label for the artisan in simple language.")

class InteractiveQuestion(BaseModel):
    question_id: str = Field(description="Unique snake_case identifier, e.g., 'confirm_silk_type', 'raw_material_clay_qty'.")
    question_text: str = Field(description="Clear, respectful question for the artisan.")
    question_type: str = Field(description="Input type: 'single_choice', 'multiple_choice', 'text_input', or 'number_input'.")
    options: Optional[List[QuestionOption]] = Field(default=None, description="Preset choices if single_choice or multiple_choice.")
    is_required: bool = Field(default=True, description="Whether this information is required for pricing or listing.")
    explanation_tip: Optional[str] = Field(default=None, description="Brief note explaining why this detail is needed.")

class ProductQuestionnaire(BaseModel):
    product_title_suggestion: str = Field(description="Suggested product title based on confirmed user input and visual analysis.")
    confirmed_user_facts: List[str] = Field(description="List of details confirmed directly from the user's text description that will NOT be asked again.")
    visual_assumptions_to_verify: List[str] = Field(description="Visual predictions from LLM analysis that need explicit artisan confirmation.")
    questions: List[InteractiveQuestion] = Field(description="3 to 5 targeted questions for material confirmation, raw material breakdown, and listing details.")


def generate_artisan_questions(
    llm_visual_analysis: dict, 
    user_description: str = "", 
    max_retries: int = 3
) -> dict:
    """
    Compares the user description against visual LLM predictions:
    1. Ignores facts explicitly mentioned by the user.
    2. Asks for confirmation on visual LLM assumptions (e.g., predicted materials/weave).
    3. Collects raw material breakdown (types and quantities) for downstream ML cost estimation.
    4. Gathers missing non-visual e-commerce specs (e.g., exact dimensions, care instructions).
    """

    major_category = llm_visual_analysis.get("major_category", "General Craft")
    sub_category = llm_visual_analysis.get("sub_category", "General")
    materials = llm_visual_analysis.get("materials_detected", [])
    features = llm_visual_analysis.get("visual_features", [])
    brief_summary = llm_visual_analysis.get("brief_summary", "")

    prompt = f"""
    You are an AI cataloging assistant for Indian micro-entrepreneurs, artisans, and weavers.
    Your goal is to prepare questions to confirm product specs and collect raw material data for price estimation.

    --- LLM VISUAL EXTRACTION ANALYSIS (UNCONFIRMED ESTIMATES) ---
    Major Category: {major_category}
    Sub-Category: {sub_category}
    Detected Materials: {', '.join(materials) if materials else 'None'}
    Detected Features: {', '.join(features) if features else 'None'}
    Visual Summary: {brief_summary}

    --- USER PROVIDED DESCRIPTION (CONFIRMED FACTS) ---
    "{user_description if user_description.strip() else 'No description provided by user.'}"

    --- DEDUCTION & QUESTION RULES ---
    1. **USER DESCRIPTION OVERRIDES**: Parse the user's description. If the user ALREADY stated a fact (e.g., "Pure Mulberry Silk", "Height 10 inches"), TREAT IT AS A CONFIRMED FACT. DO NOT ask the user to confirm or repeat this information.
    2. **LLM VISUAL CONFIRMATION**: If an attribute was detected ONLY by the LLM visual analysis (e.g., LLM saw "Terracotta / Clay"), generate a confirmation question asking the artisan to verify or specify the exact grade/type (e.g., "The image looks like Terracotta. Is this Pure Red Clay, Black Clay, or Ceramic?").
    3. **RAW MATERIAL & QUANTITY BREAKDOWN**: Ask for specific raw materials and exact quantities/units required to produce 1 unit of this item (e.g., weight of clay in grams/kg, meters of thread, volume of natural dye) so the cost can be processed by an ML model.
    4. **E-COMMERCE LISTING SPECS**: Ask for critical missing non-visual attributes required for online listing (e.g., dimensions, care instructions, crafting duration).

    Generate 3 to 5 clear, user-friendly questions with preset choices (`single_choice` / `multiple_choice`) wherever applicable.
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
                print(f"[!] API error encountered, retrying ({attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e


if __name__ == "__main__":
    # Visual extraction performed by image analysis model
    sample_llm_visual_analysis = {
        "is_valid_artisan_product": True,
        "major_category": "3. Pottery & Terracotta",
        "sub_category": "Decorative pots",
        "materials_detected": ["Terracotta", "Clay", "Natural Pigment"],
        "visual_features": ["Hand-painted floral motifs", "Earthy red tone"],
        "brief_summary": "Handcrafted earthen terracotta pot with traditional floral hand-paintings."
    }

    # User already mentioned material type (organic red clay) and height (12 inches)
    sample_user_description = "Handmade terracotta pot using organic red clay. Height is 12 inches."

    print("[+] Analyzing inputs and generating targeted questions...")
    questions_data = generate_artisan_questions(
        llm_visual_analysis=sample_llm_visual_analysis, 
        user_description=sample_user_description
    )

    print("\n--- GENERATED QUESTIONNAIRE ---")
    print(json.dumps(questions_data, indent=2))