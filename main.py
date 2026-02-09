import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from services import cartesia_svc, deepgram_svc, openai_svc

load_dotenv()

app = FastAPI(title="Interview Platform MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: session_id -> { "role": str, "questions": list[str] }
sessions: dict[str, dict] = {}


class SessionCreate(BaseModel):
    role_description: str


@app.post("/api/session")
async def create_session(body: SessionCreate):
    """Create a session: generate questions from role, return session_id and num_questions."""
    role_description = (body.role_description or "").strip()
    if not role_description:
        raise HTTPException(status_code=400, detail="role_description is required")
    try:
        questions = openai_svc.generate_questions(role_description.strip())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to generate questions: {e}")
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"role": role_description.strip(), "questions": questions}
    return {"session_id": session_id, "num_questions": len(questions), "questions": questions}


@app.get("/api/session/{session_id}/question/{index}/audio")
async def get_question_audio(session_id: str, index: int):
    """Return TTS audio (MP3) for the question at index, with emotion."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[session_id]
    questions = session["questions"]
    if index < 0 or index >= len(questions):
        raise HTTPException(status_code=404, detail="Question index out of range")
    text = questions[index]
    emotion = cartesia_svc.get_emotion_for_index(index)
    try:
        audio_bytes = cartesia_svc.text_to_speech(text, emotion=emotion)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS failed: {e}")
    return Response(content=audio_bytes, media_type="audio/mpeg")


@app.post("/api/answer")
async def submit_answer(
    session_id: str = Form(...),
    question_index: str = Form(...),
    transcript: str | None = Form(None),
    audio: UploadFile | None = File(None),
):
    """Judge answer: use transcript if provided, else transcribe audio. Return transcript, score, feedback."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[session_id]
    questions = session["questions"]
    try:
        idx = int(question_index)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid question_index")
    if idx < 0 or idx >= len(questions):
        raise HTTPException(status_code=404, detail="Question index out of range")
    question = questions[idx]

    if transcript and transcript.strip():
        transcript_text = transcript.strip()
    elif audio and audio.filename:
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="No audio data")
        try:
            transcript_text = deepgram_svc.transcribe_audio(audio_bytes)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Transcription failed: {e}")
    else:
        raise HTTPException(status_code=400, detail="Provide transcript or audio")

    try:
        result = openai_svc.judge_answer(session["role"], question, transcript_text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Judging failed: {e}")
    score = result.get("score", 0)
    feedback = result.get("feedback", "")
    return {"transcript": transcript_text, "score": score, "feedback": feedback}


@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio to text via Deepgram. Returns { transcript: str }."""
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No audio data")
    try:
        transcript = deepgram_svc.transcribe_audio(audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Transcription failed: {e}")
    return {"transcript": transcript}


# Serve frontend for demo
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
