# Biblioteko - Maintenance Manual

This manual is intended for System Administrators and Developers responsible for maintaining the Biblioteko digital library system.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Routine Maintenance Tasks](#2-routine-maintenance-tasks)
3. [Backup & Recovery](#3-backup--recovery)
4. [Security & Updates](#4-security--updates)
5. [Logs & Monitoring](#5-logs--monitoring)
6. [Emergency Procedures](#6-emergency-procedures)

---

## 1. System Overview

### Architecture

- **Backend:** Python 3.9+ (Pyramid Framework).
- **Database:** JSON flat files located in `bibliotheque_data/`.
- **Storage:** Local file system (`bibliotheque_data/` subfolders).
- **External Service:** Google Gemini API (AI analysis).

### Key Directories

| Path                             | Description                    | Criticality  |
| :------------------------------- | :----------------------------- | :----------- |
| `src/`                           | Application source code        | High         |
| `bibliotheque_data/users.json`   | User database & RBAC roles     | **Critical** |
| `bibliotheque_data/fond_commun/` | Public PDF files (unencrypted) | High         |
| `bibliotheque_data/sequestre/`   | Private PDF files (encrypted)  | High         |
| `bibliotheque_data/a_moderer/`   | Pending uploads (temporary)    | Medium       |

---

## 2. Routine Maintenance Tasks

### Daily/Weekly Checks

1.  **Disk Space**: Ensure sufficient space for new PDF uploads.
2.  **API Quota**: Check Google Gemini API usage to avoid hitting rate limits.
3.  **Moderation Queue**: Ensure the `a_moderer` folder isn't accumulating corrupt files (see Troubleshooting).

### Annual Tasks (Cron Job)

- **Rights Expiration**: Run the rights checker to move eligible works to the Public Domain.
  ```bash
  python cli.py check_rights
  ```
  _Recommendation: Schedule this via `cron` (Linux) or Task Scheduler (Windows) for January 1st._

---

## 3. Backup & Recovery

Since Biblioteko uses a flat-file system, backups are straightforward.

### Backup Procedure

1.  Stop the web server.
2.  Copy the entire `bibliotheque_data` folder to a secure, remote location.
    ```bash
    cp -r bibliotheque_data /path/to/backup/biblioteko_backup_$(date +%F)
    ```
3.  Restart the server.

### Restoration Procedure

1.  Stop the server.
2.  Delete the current `bibliotheque_data` folder.
    ```bash
    rm -rf bibliotheque_data
    ```
3.  Restore the backup folder.
4.  Ensure file permissions allow the Python process to read/write.
5.  Restart the server.

---

## 4. Security & Updates

### Updating Dependencies

Regularly update Python packages to patch security vulnerabilities.

```bash
source venv/bin/activate
pip install --upgrade pyramid waitress google-generativeai
pip freeze > requirements.txt
```

## Rotating Secrets

API Key: If the Google Gemini API key is compromised:

- Revoke it in the Google Cloud Console.

- Generate a new key.

- Update the .env file immediately.

- Restart the server.

## Session Secret:

If you need to force a logout for all users (e.g., after a suspected breach):

- Open src/app/interface/web/**init**.py.

- Change the secret string in this line:

```python
my_session_factory = SignedCookieSessionFactory('NEW_SUPER_SECRET_KEY')
```

- Restart the server. All existing session cookies will become invalid.

## 5. Logs & Monitoring

Application Logs
Biblioteko prints system logs directly to the standard output (console).

- Production Setup: It is highly recommended to redirect output to a file for long-term persistence and debugging.

Run in background and append to biblioteko.log

```bash
python main_web.py >> biblioteko.log 2>&1 &
```

- Searching for Errors: Use grep (Linux/Mac) or a text editor to look for specific keywords like "Error", "Exception", or "Traceback".

```bash
tail -f biblioteko.log | grep -i "Error"
```

Common Log Messages & Meanings
✅ AI Adapter loaded: The system started successfully and connected to the Google API.

⚠️ JSON invalide or ⚠️ Corrupt file: The AI returned malformed data or a file is unreadable. The system usually skips these automatically to prevent crashing.

❌ Erreur critique: A severe application failure occurred (e.g., missing permissions, disk full). Investigation is required.

## 6. Emergency Procedures

### Scenario A: Moderation Page is Crashing (Error 500)

- Symptoms: The administrator cannot access the /moderation page; the server returns an "Internal Server Error".

- Diagnosis: A corrupt JSON file (often caused by invalid AI output containing unescaped characters) exists in the pending queue and is blocking the file listing function.

- Fix:

1. Stop the web server.

2. Navigate to the directory bibliotheque_data/a_moderer/.

3. Delete all files (.json and .pdf) inside this folder.

4. Restart the web server.

5. The moderation page should now load (empty).

### Scenario B: User Permissions are Broken ("Access Denied")

- Symptoms: Users cannot submit files despite being logged in. The logs show PermissionError: Access denied.

- Diagnosis: This usually happens if the source code regarding Roles/Permissions (RBAC) was updated, but the users.json database file still contains old user data structures lacking the new permission fields.

- Fix:

1. Backup bibliotheque_data/users.json (optional, for reference).

2. Delete the file bibliotheque_data/users.json.

3. Restart the web server.

- Note: This triggers the automatic recreation of the default Admin account.

4. Instruct all users to re-register their accounts via the /signup page.
