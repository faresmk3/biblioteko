import os
import google.generativeai as genai
from core.ports import OCRProvider
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GeminiAdapter(OCRProvider):
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ GOOGLE_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        # Use a model capable of multimodal processing (PDF + Text)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

    def extraire_texte(self, fichier_stream) -> str:
        """
        Uploads the file stream to Gemini and requests a Markdown conversion.
        """
        try:
            # 1. Read the stream data
            if hasattr(fichier_stream, 'seek'):
                fichier_stream.seek(0)
            file_data = fichier_stream.read()

            # 2. Prepare the prompt
            prompt = """
            You are an expert OCR system. 
            Please extract all the text from this PDF document.
            Format the output strictly in Markdown.
            Preserve headers, lists, and structure.
            Do not add any conversational text (no "Here is the text", etc.), just the content.
            """

            # 3. Generate content
            # Gemini accepts bytes directly for common formats like PDF
            response = self.model.generate_content([
                {'mime_type': 'application/pdf', 'data': file_data},
                prompt
            ])

            # 4. Return text
            return response.text

        except Exception as e:
            print(f"❌ AI Error: {e}")
            return f"Error during OCR processing: {str(e)}"