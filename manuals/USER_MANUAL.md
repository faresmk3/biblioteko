# Biblioteko - User Manual

**Biblioteko** is a secure digital library system with AI-assisted moderation and rights management.

---

## Table of Contents

1. [Installation & Setup](#1-installation--setup)
2. [Web Interface Guide](#2-web-interface-guide)
3. [Administrator Guide](#3-administrator-guide)
4. [Command Line Interface (CLI)](#4-command-line-interface-cli)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Installation & Setup

/ ! \ On windows you might want to write `python` when executing some commands on windows since sometimes writing `python3` makes windows not recognise the command and tell you that python doesn't exist or is not installed.

### Prerequisites

- **Python 3.9** or higher.
- A **Google Gemini API Key** (for automatic metadata extraction).

### Step-by-Step Installation

1.  **Open your terminal** in the project folder.

2.  **Create and Activate Virtual Environment**:

    - _Windows_:
      ```powershell
      python -m venv venv
      venv\Scripts\activate
      ```
    - _Mac/Linux_:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Install Dependencies**:

    ```bash
    pip install pyramid waitress google-generativeai python-dotenv chameleon
    ```

4.  **Set up API Key**:
    Create a file named `.env` in the root folder and add this line:

    ```ini
    GOOGLE_API_KEY=AIzaSy... (Your actual key)
    ```

5.  **Initialize the Database**:
    This command creates the necessary folders and the default Admin account.

    ```bash
    python cli.py init
    ```

6.  **Start the Server**:

    ```bash
    python main_web.py
    ```

    Open your browser at: **`http://localhost:6543`**

7.  To make things easier, there is a file called `requirements.txt` that includes all the dependencies needed for this to work, all you need to do is write in the terminal while also being in the root directory of the project and execute the following command :

_Mac/Linux_:

```bash
pip install -r requirements.txt
```

same command for windows machines.

---

## 2. Web Interface Guide

### Registration & Login

- **Sign Up**: Click "S'inscrire". New accounts are automatically assigned the **Member** role (Can submit works and borrow books).
- **Login**: Use your email and password.
  - _Default Admin_: `admin@biblio.com` / `admin123`

### Submitting a Work (Upload)

1.  Navigate to the **"Dépôt"** (Submit) page.
2.  (Optional) Enter Title and Author. If left blank, AI will attempt to detect them.
3.  Select a **PDF file** from your computer.
4.  Click **"Soumettre"**.
    - _Note_: The AI analyzes the text to determine copyright status (Public Domain vs. Private).

### Browsing & Borrowing

The catalog is divided into two sections:

- ** Public Domain**: Free works. You can view the PDF or the extracted Markdown text immediately.
- ** Sequestered (Private)**: Copyrighted works. The file is encrypted on the server.
  - **To Read**: Click **"Emprunter"** (Borrow). The book moves to your "My Active Loans" section.
  - **Reading**: Click **"Lire"** to decrypt and view the PDF in your browser.

---

## 3. Administrator Guide

_Access restricted to users with the `admin` role._

### The Moderation Panel (`/moderation`)

When a user uploads a file, it goes to the **"À Modérer"** queue.

1.  **AI Analysis**: The system displays extracted metadata and an AI recommendation (e.g., "Author died in 1900 -> Public Domain").
2.  **Edit Metadata**: You can correct the Title, Author, or Categories.
3.  **Set Legal Status**:
    - **🔒 Sous Droits**: Encrypts the file (Borrowing required).
    - **🌍 Domaine Public**: File is open to everyone.
4.  **Action**:
    - **Valider (Approve)**: Process the file.
    - **Rejeter (Reject)**: Delete the file.

### Automatic Rights Management

Works can be automatically moved to the Public Domain if their publication date is old enough (> 70 years).

- **URL**: `http://localhost:6543/admin/check_rights`

---

## 4. Command Line Interface (CLI)

You can manage the system without a browser using `cli.py`.

| Command        | Description                 | Example                                                    |
| :------------- | :-------------------------- | :--------------------------------------------------------- |
| `init`         | Resets DB and creates Admin | `python cli.py init`                                       |
| `register`     | Create a new user           | `python cli.py register "Name" "email" "pass"`             |
| `submit`       | Upload a PDF                | `python cli.py submit "email" "file.pdf" "Title" "Author"` |
| `list_pending` | Show moderation queue       | `python cli.py list_pending`                               |
| `check_rights` | Run rights expiration check | `python cli.py check_rights`                               |

---

## 5. Troubleshooting

### "Access Denied" when submitting

- **Cause**: The user account lacks the `peut_proposer_oeuvre` permission.
- **Fix**: If you updated the code recently, delete `bibliotheque_data/users.json` and restart the server to recreate users with the correct Role structure.

### Error 500 on Moderation Page

- **Cause**: A corrupt JSON file (invalid AI output) is in the data folder.
- **Fix**: Go to `bibliotheque_data/a_moderer/` and delete all `.json` and `.pdf` files manually.

### PDF Link Returns 404

- **Cause**: Incorrect URL prefix.
- **Fix**: Ensure your template uses `/data/` and not `/static/` for file links.
