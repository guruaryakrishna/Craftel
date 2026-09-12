import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set in your environment!")

client = Groq(api_key=api_key)


def transcribe_audio(
    file_path: str, 
    language: str = None, 
    prompt: str = None
) -> str:
    """
    Transcribes audio file to text using Groq's Whisper API (`whisper-large-v3`).
    
    :param file_path: Local path to the audio file (.mp3, .wav, .m4a, .webm, etc.).
    :param language: Optional ISO language code (e.g., 'te' for Telugu, 'hi' for Hindi, 'en' for English).
                     If None, Whisper auto-detects the spoken language.
    :param prompt: Optional contextual prompt to guide technical/regional terms or specific accents.
    :return: Transcribed text string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found at path: {file_path}")

    try:
        with open(file_path, "rb") as audio_file:
            # Build API parameters
            params = {
                "file": (os.path.basename(file_path), audio_file),
                "model": "whisper-large-v3",
                "response_format": "text",  # Options: "text", "json", "verbose_json"
                "temperature": 0.0
            }
            
            # Add optional language hint if provided
            if language:
                params["language"] = language
                
            # Add optional prompt context hint if provided
            if prompt:
                params["prompt"] = prompt
    
            transcription = client.audio.transcriptions.create(**params)
            return transcription

    except Exception as e:
        print(f"[!] Groq Whisper Transcription Error: {e}")
        return ""


if __name__ == "__main__":
    # Test with a local audio file
    sample_audio_path = r"C:\coding\projects\Craftel\test\telugu_sample.mp3"  # Replace with your actual file path

    if os.path.exists(sample_audio_path):
        print("[+] Transcribing audio...")
        
        # Example 1: Auto-detect language
        text_auto = transcribe_audio(sample_audio_path)
        print("\n--- TRANSCRIPTION (Auto-detect) ---")
        print(text_auto)
        
        # Example 2: Hint for regional terms/accents using the prompt parameter
        context_prompt = "Indian handloom artisan describing saree material, silk, zari, terracotta, pot, weave."
        text_guided = transcribe_audio(sample_audio_path, prompt=context_prompt)
        print("\n--- TRANSCRIPTION (Context Guided) ---")
        print(text_guided)
    else:
        print(f"[!] Please place a valid audio file at '{sample_audio_path}' to test.")