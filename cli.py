import sys
import os
import argparse
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# 2. Path Setup
sys.path.insert(0, os.path.abspath("src/app"))

# 3. Imports
from infrastructure.repositories import FileSystemOeuvreRepository
from infrastructure.users_repo import FileSystemUserRepository
from services.service_oeuvre import ServiceOeuvre
from services.service_auth import ServiceAuth
from services.service_emprunt import ServiceEmprunt

def main():
    parser = argparse.ArgumentParser(description="Biblioteko CLI - Full Control")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # --- SYSTEM & AUTH ---
    subparsers.add_parser("init", help="Initialize system and default admin")
    
    # register <name> <email> <password>
    p_reg = subparsers.add_parser("register", help="Register a new member")
    p_reg.add_argument("name", help="User Name")
    p_reg.add_argument("email", help="User Email")
    p_reg.add_argument("password", help="User Password")

    # --- SUBMISSION ---
    # submit <user_email> <file_path> <title> <author> --cats [list]
    p_sub = subparsers.add_parser("submit", help="Submit a new work (PDF)")
    p_sub.add_argument("email", help="Member Email")
    p_sub.add_argument("filepath", help="Path to PDF file")
    p_sub.add_argument("title", help="Work Title")
    p_sub.add_argument("author", help="Author Name")
    p_sub.add_argument("--cats", nargs='+', default=[], help="List of categories (e.g. Livres Musique)")

    # --- MODERATION ---
    subparsers.add_parser("list_pending", help="[Admin] List works waiting for validation")

    # validate <admin_email> <work_id> <public|private>
    p_val = subparsers.add_parser("validate", help="[Admin] Validate a work")
    p_val.add_argument("admin_email", help="Admin Email")
    p_val.add_argument("work_id", help="ID of the work")
    p_val.add_argument("rights", choices=['public', 'private'], help="Rights status")
    
    # reject <admin_email> <work_id>
    p_rej = subparsers.add_parser("reject", help="[Admin] Reject a work")
    p_rej.add_argument("admin_email", help="Admin Email")
    p_rej.add_argument("work_id", help="ID of the work")

    # --- CATALOG & BORROWING ---
    # catalog <public|borrowable>
    p_cat = subparsers.add_parser("catalog", help="List works in catalog")
    p_cat.add_argument("type", choices=['public', 'borrowable'], help="Type of catalog")

    # borrow <user_email> <work_id>
    p_bor = subparsers.add_parser("borrow", help="Borrow a restricted work")
    p_bor.add_argument("email", help="Member Email")
    p_bor.add_argument("work_id", help="Work ID")

    # my_loans <user_email>
    p_loans = subparsers.add_parser("my_loans", help="List active loans for a user")
    p_loans.add_argument("email", help="Member Email")

    # --- AUTOMATION ---
    subparsers.add_parser("check_rights", help="[Cron] Check for expired copyrights")

    args = parser.parse_args()

    # --- INITIALIZATION ---
    base_path = os.path.abspath("bibliotheque_data")
    if not os.path.exists(base_path): os.makedirs(base_path)

    repo_oeuvre = FileSystemOeuvreRepository(base_path)
    repo_user = FileSystemUserRepository(base_path)
    
    svc_oeuvre = ServiceOeuvre(repo_oeuvre)
    svc_auth = ServiceAuth(repo_user)
    svc_emprunt = ServiceEmprunt(repo_oeuvre, base_path)

    # --- EXECUTION LOGIC ---

    if args.command == "init":
        print("[*] Initializing system...")
        svc_auth.ensure_admin_exists()
        print("[+] System ready. Admin created.")

    elif args.command == "register":
        try:
            user = svc_auth.inscrire_membre(args.name, args.email, args.password)
            print(f"[+] User created: {user.nom} ({user.id})")
        except Exception as e:
            print(f"[!] Error: {e}")

    elif args.command == "submit":
        if not os.path.exists(args.filepath):
            print(f"[!] File not found: {args.filepath}")
            return
        
        user = repo_user.trouver_par_email(args.email)
        if not user:
            print("[!] User not found.")
            return

        try:
            print("[*] Processing submission (OCR in progress)...")
            with open(args.filepath, 'rb') as f:
                # Service expects a file-like object
                oeuvre = svc_oeuvre.soumettre_oeuvre(user, args.title, args.author, args.cats, f)
            print(f"[+] Work submitted: {oeuvre.titre} (ID: {oeuvre.id})")
        except Exception as e:
            print(f"[!] Error: {e}")

    elif args.command == "list_pending":
        # We need an admin to view this list
        admin = repo_user.trouver_par_email("admin@biblio.com") 
        if not admin: 
            print("[!] Default admin not found. Run 'init'.")
            return
        
        try:
            oeuvres = svc_oeuvre.lister_a_moderer(admin)
            print(f"--- Pending Works ({len(oeuvres)}) ---")
            for o in oeuvres:
                print(f"ID: {o.id} | Title: {o.titre} | Author: {o.auteur_nom} | Cats: {o.categories}")
        except Exception as e:
            print(f"[!] Error: {e}")

    elif args.command == "validate":
        admin = repo_user.trouver_par_email(args.admin_email)
        if not admin:
            print("[!] Admin user not found.")
            return
        
        is_public = (args.rights == 'public')
        try:
            svc_oeuvre.valider_oeuvre(admin, args.work_id, is_public)
            print(f"[+] Work {args.work_id} validated as {args.rights}.")
        except Exception as e:
            print(f"[!] Error: {e}")

    elif args.command == "reject":
        admin = repo_user.trouver_par_email(args.admin_email)
        if not admin:
            print("[!] Admin user not found.")
            return
        try:
            svc_oeuvre.rejeter_oeuvre(admin, args.work_id)
            print(f"[-] Work {args.work_id} rejected and archived.")
        except Exception as e:
            print(f"[!] Error: {e}")

    elif args.command == "catalog":
        if args.type == "public":
            works = svc_oeuvre.lister_publiques()
            print(f"--- Public Domain Catalog ({len(works)}) ---")
            for w in works:
                print(f"[{w.id}] {w.titre} by {w.auteur_nom}")
        else:
            works = svc_oeuvre.lister_sequestre()
            print(f"--- Borrowable Catalog ({len(works)}) ---")
            for w in works:
                print(f"[{w.id}] {w.titre} by {w.auteur_nom}")

    elif args.command == "borrow":
        user = repo_user.trouver_par_email(args.email)
        if not user:
            print("[!] User not found.")
            return
        try:
            svc_emprunt.emprunter(user, args.work_id)
            print(f"[+] Borrow successful for {args.work_id}.")
        except Exception as e:
            print(f"[!] Error: {e}")

    elif args.command == "my_loans":
        user = repo_user.trouver_par_email(args.email)
        if not user:
            print("[!] User not found.")
            return
        loans = svc_emprunt.lister_mes_emprunts(user)
        print(f"--- Active Loans for {user.nom} ---")
        for l in loans:
            print(f"Title: {l['work_title']} | Return by: {l['end_date']}")

    elif args.command == "check_rights":
        svc_oeuvre.verifier_expiration_droits()
        print("[+] Automatic rights check completed.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()