import os
import json
from groq import Groq
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set in your environment!")

client = Groq(api_key=api_key)


class DynamicTranslationOutput(BaseModel):
    translated_text: str = Field(description="The translated text in the target language.")


def translate_text(text: str, target_lang: str) -> str:
    """
    Translates any input text into the specified target language using Groq API.
    
    :param text: Text to translate.
    :param target_lang: Target language code or name (e.g., 'hi', 'en', 'te', 'Hindi', 'Telugu').
    :return: Translated text string.
    """
    if not text or not text.strip():
        return ""

    prompt = f"""
    You are a professional multilingual translator.
    Translate the following text into target language: "{target_lang}".
    Keep the translation natural, accurate, and contextually correct.

    Respond STRICTLY with a JSON object adhering to this JSON Schema:
    {json.dumps(DynamicTranslationOutput.model_json_schema())}

    --- TEXT TO TRANSLATE ---
    "{text}"
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result_content = response.choices[0].message.content
        data = json.loads(result_content)
        return data.get("translated_text", text)
        
    except Exception as e:
        print(f"[!] Groq Translation error: {e}")
        return text


if __name__ == "__main__":
    statement = "ఈ మట్టి పాత్ర చేతితో తయారు చేయబడింది."

    # Translate to Hindi
    hindi_text = translate_text(statement, target_lang="Hindi")
    print("Hindi  :", hindi_text)

    # Translate to English
    english_text = translate_text(statement, target_lang="English")
    print("English:", english_text)

    # Translate to Tamil
    tamil_text = translate_text(statement, target_lang="Tamil")
    print("Tamil  :", tamil_text)