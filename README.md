## Backend (FastAPI) – Setup & Run

This directory contains the **FastAPI** backend for the Interview Platform MVP.

---

## 1. Create and activate a virtual environment

From the **project root** or from inside `backend/`, run:

```bash
cd backend

# Create virtual environment (Python 3.10+)
python -m venv .venv

# Activate (macOS / Linux)
source .venv/bin/activate

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows Command Prompt)
.venv\Scripts\activate
```

You should now see `(.venv)` in your shell prompt.

---

## 2. Install Python dependencies

With the virtual environment **activated** and your working directory in `backend/`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, and the SDKs for Deepgram, Cartesia, and OpenAI.

---

## 3. Configure environment variables

Copy the example env file and fill in your API keys:

```bash
cd backend   # if not already here
cp .env.example .env
```

Then open `.env` in your editor and set:

- `DEEPGRAM_API_KEY` – Deepgram API key (speech-to-text)
- `CARTESIA_API_KEY` – Cartesia API key (text-to-speech)
- `OPENAI_API_KEY` – OpenAI API key (question generation + judging)

> **Do not commit** real keys to version control.

---

## 4. Run the FastAPI server

With the virtual environment **activated** and your working directory in `backend/`:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This starts the backend on `http://localhost:8000`.

- **Swagger UI** (interactive API docs): `http://localhost:8000/docs`
- **ReDoc** docs: `http://localhost:8000/redoc`

Depending on how you run the frontend, the backend may also serve the built frontend at the root URL.

---

## 5. Useful commands

- **Check installed packages**:

  ```bash
  pip list
  ```

- **Freeze dependencies to a file** (if you add new packages):

  ```bash
  pip freeze > requirements.txt
  ```

- **Deactivate the virtual environment**:

  ```bash
  deactivate
  ```

