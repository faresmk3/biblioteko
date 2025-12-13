# check_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("🔍 Recherche des modèles disponibles pour votre clé...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Dispo : {m.name}")
except Exception as e:
    print(f"❌ Erreur : {e}")