## Interview Flow – Frontend ↔ Backend APIs

This doc explains how a frontend client should call the backend APIs in order during a typical interview session.

High‑level flow:

1. Create a session (you can provide your own questions).
2. Show questions in the UI.
3. For each question:
   - Play question audio (TTS).
   - Capture the candidate's answer (audio and/or text).
   - (Optional) Get raw transcript only.
   - Submit answer to be judged.
4. Show score and feedback.

---

## 1. Create session (with provided questions)

**Recommended for custom UIs**: you control the copy and number of questions.

- **Endpoint**: `POST /api/session/with-questions`

**Request body (JSON)**:

```json
{
  "role_description": "Senior frontend engineer specializing in React",
  "num_questions": 3,
  "questions": [
    "Tell me about a challenging frontend performance problem you solved.",
    "How do you structure large React applications?",
    "How do you approach accessibility in React?"
  ]
}
```

**Response (JSON)**:

```json
{
  "session_id": "uuid-here",
  "num_questions": 3,
  "questions": [
    "Tell me about a challenging frontend performance problem you solved.",
    "How do you structure large React applications?",
    "How do you approach accessibility in React?"
  ]
}
```

The frontend should:

- Store `session_id`.
- Store `questions` locally (e.g., React state).
- Use `num_questions`/`questions.length` to drive pagination / progress UI.

> Alternative: Use `POST /api/session` to let the backend generate questions from `role_description` automatically.

---

## 2. Show questions

Use the `questions` array from the session response:

- Index `0` → first question
- Index `1` → second question
- ...
- Index `i` → current question index used in later API calls

No API call is required just to "show" a question — you already have the text.

---

## 3. Play question audio (TTS)

For each question you want to play aloud:

- **Endpoint**: `GET /api/session/{session_id}/question/{index}/audio`
- **Response**: `audio/mpeg` (MP3 bytes)

Frontend usage:

1. Build the URL, e.g. `http://localhost:8000/api/session/<session_id>/question/<index>/audio`.
2. `fetch` it as a `blob`.
3. Create an `Audio` object or `audio` element and play the blob.

Pseudocode:

```ts
const res = await fetch(
  `${API_BASE}/api/session/${sessionId}/question/${questionIndex}/audio`
);
const blob = await res.blob();
const url = URL.createObjectURL(blob);
const audio = new Audio(url);
audio.play();
```

---

## 4. Capture answer (frontend)

The frontend is responsible for recording audio and/or collecting a text answer:

- **Option A** – mic recording only:
  - Record audio in the browser (e.g., MediaRecorder → Blob).
  - Send audio file to backend.
- **Option B** – text only:
  - Use a textarea or input to collect the answer.
  - Send as `transcript` only.
- **Option C** – both:
  - Send both; backend will **prefer `transcript`** if it is non‑empty.

---

## 5. (Optional) Get transcript only (STT)

If you want **just the transcript** first (e.g., to show a live transcript before scoring), you can call the STT endpoint directly:

- **Endpoint**: `POST /api/transcribe`
- **Content‑Type**: `multipart/form-data` with an `audio` file.

**Response**:

```json
{
  "transcript": "This is the transcribed audio."
}
```

You can then show the transcript in the UI, and later send it as `transcript` to `/api/answer` (no need to send audio again).

---

## 6. Submit answer (get score + feedback)

- **Endpoint**: `POST /api/answer`
- **Content‑Type**: `multipart/form-data`

**Form fields**:

- `session_id` – from step 1.
- `question_index` – zero‑based index for the current question.
- `transcript` (optional) – text answer. If present and non‑empty, audio will be ignored.
- `audio` (optional) – audio file (Blob/File) of the answer.

**Frontend examples**:

### A. Text‑only answer

```ts
const form = new FormData();
form.append("session_id", sessionId);
form.append("question_index", String(questionIndex));
form.append("transcript", answerText);

const res = await fetch(`${API_BASE}/api/answer`, {
  method: "POST",
  body: form,
});
const data = await res.json();
```

### B. Audio‑only answer

```ts
const form = new FormData();
form.append("session_id", sessionId);
form.append("question_index", String(questionIndex));
form.append("audio", audioFile); // Blob or File from MediaRecorder

const res = await fetch(`${API_BASE}/api/answer`, {
  method: "POST",
  body: form,
});
const data = await res.json();
```

**Response**:

```json
{
  "transcript": "I once improved a React app's TTFB by...",
  "score": 4,
  "feedback": "Strong answer with clear examples. Consider also touching on trade-offs."
}
```

The frontend should:

- Display `transcript` (if useful for review).
- Show `score` prominently (e.g., numeric badge or progress meter).
- Show `feedback` as detailed explanation text.

---

## 7. Moving to next question

On the frontend:

1. Increment `questionIndex` in state.
2. Read the next question from the `questions` array.
3. Optionally call the TTS endpoint again for the new index.
4. Repeat **capture → (optional STT) → submit answer**.

Stop when `questionIndex + 1 === num_questions`; show an "Interview complete" screen.

---

## 8. Summary of API sequence

For a full session:

1. **Create session**  
   `POST /api/session/with-questions`
2. **Show question text**  
   Use `questions[index]` from the session response.
3. **Play TTS**  
   `GET /api/session/{session_id}/question/{index}/audio`
4. **Record answer (frontend)**  
   Browser APIs (MediaRecorder / text input).
5. **(Optional) Raw STT**  
   `POST /api/transcribe`
6. **Submit answer and get score**  
   `POST /api/answer`
7. **Repeat for all questions**, then show final results.

