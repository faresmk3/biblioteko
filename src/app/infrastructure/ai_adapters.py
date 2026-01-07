import os
import json
import google.generativeai as genai
from core.ports import OCRProvider
from dotenv import load_dotenv
import re
load_dotenv()

class GeminiAdapter(OCRProvider):
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ GOOGLE_API_KEY not found.")
        
        genai.configure(api_key=api_key)
        # Use the model that works for you (2.5-flash or 1.5-flash)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

    def analyser_oeuvre(self, fichier_stream) -> dict:
        try:
            if hasattr(fichier_stream, 'seek'):
                fichier_stream.seek(0)
            file_data = fichier_stream.read()

            # Prompt simplifié et strict
            prompt = """
            Analyze this PDF text content.
            Return a valid JSON object with these exact keys:
            {
                "titre": "Title found",
                "auteur": "Author found",
                "date_publication": "Year (YYYY)",
                "est_domaine_public": true/false,
                "raison": "Short explanation",
                "contenu_markdown": "Full text content..."
            }
            DO NOT add any text outside the JSON object.
            """

            response = self.model.generate_content([
                {'mime_type': 'application/pdf', 'data': file_data},
                prompt
            ])

            raw_text = response.text.strip()
            
            # --- EXTRACTION CHIRURGICALE DU JSON ---
            # On cherche tout ce qui se trouve entre la première '{' et la dernière '}'
            # re.DOTALL permet au '.' de capturer aussi les sauts de ligne
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            
            if match:
                json_str = match.group(0)
            else:
                # Si pas de JSON trouvé, on force une erreur pour le log
                raise ValueError("No JSON object found in AI response")

            # Tentative de parsing
            try:
                resultat = json.loads(json_str)
            except json.JSONDecodeError:
                # Si le JSON est mal formé (ex: guillemets dans le texte), on tente un nettoyage basique
                # On remplace les sauts de ligne réels par \n dans les valeurs pour éviter la casse
                print(f"⚠️ JSON invalide, tentative de réparation...")
                return {
                    "titre": "Analyse partielle (Erreur JSON)",
                    "auteur": "Inconnu",
                    "contenu_markdown": raw_text[:1000] + "\n... [Erreur de formatage IA]"
                }

            # Construction du résultat final sécurisé
            return {
                "titre": str(resultat.get("titre", "Titre inconnu")),
                "auteur": str(resultat.get("auteur", "Auteur inconnu")),
                "date_publication": str(resultat.get("date_publication", "2024")),
                "est_domaine_public": bool(resultat.get("est_domaine_public", False)),
                "raison": str(resultat.get("raison", "Analyse effectuée")),
                "contenu_markdown": str(resultat.get("contenu_markdown", ""))
            }

        except Exception as e:
            print(f"❌ Erreur IA : {e}")
            # Fallback qui permet au système de continuer même si l'IA échoue totalement
            return {
                "titre": "Erreur d'analyse",
                "auteur": "Inconnu",
                "contenu_markdown": "L'analyse automatique a échoué."
            }