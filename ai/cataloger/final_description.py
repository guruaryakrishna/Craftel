import os
import json
import time
from typing import List, Dict, Any, Optional
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


# Pydantic Schema for E-Commerce Description
class ProductDescriptionOutput(BaseModel):
    product_title: str = Field(
        description="Optimized e-commerce title incorporating core material, craft technique, and item type."
    )
    short_description: str = Field(
        description="A ultra-concise summary of STRICTLY 4 to 6 words (e.g., 'Handcrafted Red Clay Decorative Pot')."
    )
    brief_description: str = Field(
        description="A detailed paragraph (strictly 3 to 4 sentences) covering raw materials, handcrafting process, dimensions/specifications, and care/usage instructions."
    )
    key_highlights: List[str] = Field(
        description="3 to 5 bullet points highlighting authentic features (e.g., Pure Handmade, Natural Dyes, Hand-painted)."
    )


def generate_final_product_description(
    llm_visual_analysis: Dict[str, Any],
    user_description: str = "",
    qa_responses: Optional[List[Dict[str, Any]]] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Synthesizes visual analysis, user description, and answered questionnaire data
    into a structured e-commerce product description.
    """

    qa_responses = qa_responses or []

    # Format QA pairs for prompt injection
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
    brief_summary = llm_visual_analysis.get("brief_summary", "")

    prompt = f"""
    You are an expert e-commerce copywriter specializing in Indian handicrafts, handlooms, terracotta, and artisanal products.
    Your task is to synthesize all gathered information into an engaging, customer-ready e-commerce description.

    --- SOURCE DATA ---
    1. VISUAL EXTRACTION DETAILS:
       - Major Category: {major_category}
       - Sub Category: {sub_category}
       - Visually Detected Materials: {', '.join(materials) if materials else 'None'}
       - Visual Features: {', '.join(features) if features else 'None'}
       - Visual Summary: {brief_summary}

    2. USER INITIAL DESCRIPTION:
       "{user_description if user_description.strip() else 'No initial text provided by seller.'}"

    3. ARTISAN CONFIRMED ANSWERS (HIGHEST PRIORITY FACT SOURCE):
{qa_formatted_text}

    --- INSTRUCTIONS ---
    - Combine all verified information into a cohesive, professional description.
    - Resolve any conflicts in favor of the **ARTISAN CONFIRMED ANSWERS** and **USER INITIAL DESCRIPTION**.
    - **`short_description`**: STRICTLY 4 to 6 words long. Punchy, clean title tag for cards (e.g., "Handmade Terracotta Floral Decorative Pot").
    - **`brief_description`**: Write a compelling paragraph of **STRICTLY 3 TO 4 SENTENCES**. 
      * Sentence 1: Introduce the product, craft heritage, and primary raw materials used.
      * Sentence 2: Detail the handcrafting technique, visual features, and unique artistic touch.
      * Sentence 3: State practical specifications like dimensions, weight, capacity, or weave details.
      * Sentence 4: Mention recommended usage, care instructions, or authenticity certifications.
    """

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ProductDescriptionOutput,
                    temperature=0.3
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
    sample_visual_analysis = {
        "major_category": "3. Pottery & Terracotta",
        "sub_category": "Decorative pots",
        "materials_detected": ["Terracotta", "Clay", "Natural Pigment"],
        "visual_features": ["Hand-painted floral motifs", "Earthy red tone"],
        "brief_summary": "Handcrafted earthen terracotta pot with traditional floral hand-paintings."
    }

    sample_user_desc = "Handmade terracotta pot made using organic red clay."

    sample_qa_answers = [
        {
            "question_id": "dimensions_cm",
            "question_text": "What is the height and width of the pot?",
            "answer": "Height is 12 inches and width is 8 inches."
        },
        {
            "question_id": "raw_material_clay_qty",
            "question_text": "How much raw clay was used for making this single piece?",
            "answer": "Around 1.5 kilograms of natural clay."
        }
    ]

    print("[+] Generating final product descriptions...")
    final_output = generate_final_product_description(
        llm_visual_analysis=sample_visual_analysis,
        user_description=sample_user_desc,
        qa_responses=sample_qa_answers
    )

    print("\n--- GENERATED PRODUCT CATALOGING DETAILS ---")
    print(json.dumps(final_output, indent=2))