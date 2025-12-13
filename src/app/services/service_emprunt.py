# src/app/services/service_emprunt.py
from datetime import datetime, timedelta
import os
import json
from core.auth import Utilisateur
from core.ports import OeuvreRepository

class ServiceEmprunt:
    def __init__(self, repo: OeuvreRepository, base_path: str):
        self.repo = repo
        self.loans_file = os.path.join(base_path, "active_loans.json")
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists(self.loans_file):
            with open(self.loans_file, 'w') as f: json.dump({}, f)

    def _load_loans(self):
        with open(self.loans_file, 'r') as f: return json.load(f)

    def _save_loans(self, data):
        with open(self.loans_file, 'w') as f: json.dump(data, f, indent=4)

    def emprunter(self, user: Utilisateur, id_oeuvre: str):
        # 1. Verify availability
        try:
            oeuvre = self.repo.charger(id_oeuvre, "sequestre")
        except:
            raise ValueError("Work not available for loan.")

        # 2. Register Loan
        loans = self._load_loans()
        
        # Key = UserEmail_WorkID
        loan_key = f"{user.email}_{id_oeuvre}"
        
        if loan_key in loans:
            raise ValueError("You already have this book.")

        loans[loan_key] = {
            "user": user.email,
            "work_id": id_oeuvre,
            "work_title": oeuvre.titre,
            "start_date": str(datetime.now().date()),
            "end_date": str((datetime.now() + timedelta(weeks=2)).date()) # Requirement: 2 weeks
        }
        
        self._save_loans(loans)
        print(f"✅ Loan registered for {user.nom}: {oeuvre.titre}")

    def lister_mes_emprunts(self, user: Utilisateur) -> list:
        loans = self._load_loans()
        # Filter loans for this user
        return [info for key, info in loans.items() if info["user"] == user.email]