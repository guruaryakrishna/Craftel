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

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in your environment!")

client = genai.Client(api_key=api_key)


# Pydantic Schema for Validation Output
class AnswerValidationResult(BaseModel):
    is_valid: bool = Field(
        description="True if the answer is clear, relevant, and addresses the question. False if vague, off-topic, or nonsensical."
    )
    confidence_score: float = Field(
        description="Confidence score between 0.0 and 1.0 regarding the answer validity."
    )
    extracted_value: Optional[str] = Field(
        default=None,
        description="Cleaned/structured version of the extracted value (e.g., '12 inches', 'Red Clay', '500 grams')."
    )
    reason: str = Field(
        description="Brief explanation of why the answer was marked valid or invalid."
    )
    clarification_prompt: Optional[str] = Field(
        default=None,
        description="If invalid, a short polite follow-up question asking the artisan for the missing detail in clear language."
    )


def validate_artisan_answer(
    question_text: str,
    question_type: str,
    transcribed_answer: str,
    max_retries: int = 3
) -> dict:
    """
    Validates a transcribed English answer against a specific question asked to an artisan.
    Handles noisy or ambiguous speech transcriptions.
    """

    prompt = f"""
    You are an AI data validator for an e-commerce cataloging system used by artisans and weavers.
    An automated system asked the user a question, and the user replied via voice (transcribed into English).

    --- QUESTION ASKED ---
    Question: "{question_text}"
    Expected Input Type: {question_type}

    --- TRANSCRIBED USER ANSWER ---
    "{transcribed_answer}"

    --- VALIDATION RULES ---
    1. **RELEVANCE**: Check if the user's answer directly answers the question asked.
    2. **INPUT MATCH**: If the question asks for a number or quantity (e.g., height, weight, meters, time), verify the user supplied a recognizable measurement or value.
    3. **NOISE TOLERANCE**: Voice transcriptions may have slight filler words (e.g., "uh", "like", "namaste", "I think"). Ignore conversational filler if the core answer is present.
    4. **INVALID CASES**: If the user gives a completely unrelated answer (e.g., asked for dimensions but replied with color), says "I don't know", or the transcript is gibberish, set `is_valid` to False.
    5. **CLARIFICATION**: If invalid, write a simple, polite re-prompt in `clarification_prompt` asking for the exact missing detail.
    """

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AnswerValidationResult,
                    temperature=0.1
                )
            )
            return json.loads(response.text)

        except (ServerError, APIError) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"[!] API error, retrying ({attempt + 1}/{max_retries}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e


if __name__ == "__main__":
    # Test Case 1: Valid answer with extra speech
    q1 = "What is the exact height and width of this terracotta pot?"
    a1 = "Namaste sir, the height is around 12 inches and width is 8 inches."

    # Test Case 2: Invalid / Vague answer
    q2 = "How many grams of natural organic clay do you need to make one pot?"
    a2 = "It takes around two days to paint the entire surface."

    print("[+] Validating Answer 1...")
    res1 = validate_artisan_answer(q1, "number_input", a1)
    print(json.dumps(res1, indent=2))

    print("\n[+] Validating Answer 2...")
    res2 = validate_artisan_answer(q2, "number_input", a2)
    print(json.dumps(res2, indent=2))