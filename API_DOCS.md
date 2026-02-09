## Interview Platform API

**Base URL**: `http://localhost:8000`

All endpoints are JSON-based unless otherwise noted.

---

## Authentication

No authentication is required in this MVP. Sessions are tracked via a `session_id` returned by the backend.

---

## Create Session

- **Method**: `POST`
- **Path**: `/api/session`
- **Description**: Creates a new interview session, generates questions for the given role, and returns the session metadata.

### Request Body

```json
{
  "role_description": "Senior frontend engineer specializing in React"
}
```

#### Fields

- **role_description** `string` (required): Free-text description of the role. Used to generate interview questions.

### Response: 200 OK

```json
{
  "session_id": "e0de5c0e-2e5f-4e5c-9e9c-4bcb6c991234",
  "num_questions": 5,
  "questions": [
    "Tell me about a challenging frontend performance problem you solved.",
    "How do you structure large React applications?",
    "..."
  ]
}
```

#### Fields

- **session_id** `string`: Unique identifier for this in-memory session. Required for subsequent calls.
- **num_questions** `number`: Count of generated questions.
- **questions** `string[]`: The generated questions, in order.

### Error Responses

- **400 Bad Request**

  ```json
  { "detail": "role_description is required" }
  ```

- **502 Bad Gateway**

  ```json
  { "detail": "Failed to generate questions: <reason>" }
  ```

---

## Get Question Audio

- **Method**: `GET`
- **Path**: `/api/session/{session_id}/question/{index}/audio`
- **Description**: Returns TTS audio (MP3) for the specified question in the session, with emotion applied.
- **Response Type**: `audio/mpeg` (binary)

### Path Parameters

- **session_id** `string` (required): The `session_id` returned from `/api/session`.
- **index** `integer` (required): Zero-based question index in the `questions` array.

### Successful Response: 200 OK

- Binary MP3 data (`Content-Type: audio/mpeg`).

### Error Responses

- **404 Not Found**

  ```json
  { "detail": "Session not found" }
  ```

- **404 Not Found**

  ```json
  { "detail": "Question index out of range" }
  ```

- **502 Bad Gateway**

  ```json
  { "detail": "TTS failed: <reason>" }
  ```

---

## Submit Answer

- **Method**: `POST`
- **Path**: `/api/answer`
- **Description**: Submits an answer for a given question. The answer can be provided as plain text (`transcript`) or as an audio file (`audio`). If both are provided, `transcript` is used and audio is ignored.
- **Content Type**: `multipart/form-data`

### Form Fields

- **session_id** `string` (required): The session identifier returned from `/api/session`.
- **question_index** `string` (required): Zero-based index of the question in the session. (Sent as a string in the form; parsed into an integer on the backend.)
- **transcript** `string` (optional): The text of the candidate's answer. If provided and non-empty, the backend will **not** transcribe audio.
- **audio** `file` (optional): Audio file containing the answer. Used only if `transcript` is missing or empty.

At least one of `transcript` or `audio` must be provided.

### Example Request (text-only)

`Content-Type: multipart/form-data`

Form fields:

- `session_id`: `e0de5c0e-2e5f-4e5c-9e9c-4bcb6c991234`
- `question_index`: `0`
- `transcript`: `I once improved a React app's TTFB by...`

### Example Request (audio-only)

`Content-Type: multipart/form-data`

Form fields:

- `session_id`: `e0de5c0e-2e5f-4e5c-9e9c-4bcb6c991234`
- `question_index`: `0`
- `audio`: `<binary audio file>`

### Response: 200 OK

```json
{
  "transcript": "I once improved a React app's TTFB by...",
  "score": 4,
  "feedback": "Strong answer with clear examples. Consider also touching on trade-offs."
}
```

#### Fields

- **transcript** `string`: Final transcript used for judging (either provided or transcribed).
- **score** `number`: Numeric evaluation of the answer (scale defined by the OpenAI judging prompt).
- **feedback** `string`: Natural-language feedback on the answer.

### Error Responses

- **400 Bad Request**

  ```json
  { "detail": "Invalid question_index" }
  ```

- **400 Bad Request**

  ```json
  { "detail": "Provide transcript or audio" }
  ```

- **400 Bad Request**

  ```json
  { "detail": "No audio data" }
  ```

- **404 Not Found**

  ```json
  { "detail": "Session not found" }
  ```

- **404 Not Found**

  ```json
  { "detail": "Question index out of range" }
  ```

- **502 Bad Gateway**

  ```json
  { "detail": "Transcription failed: <reason>" }
  ```

- **502 Bad Gateway**

  ```json
  { "detail": "Judging failed: <reason>" }
  ```

---

## Transcribe Audio

- **Method**: `POST`
- **Path**: `/api/transcribe`
- **Description**: Transcribes an audio file to text using Deepgram.
- **Content Type**: `multipart/form-data`

### Form Fields

- **audio** `file` (required): Audio file to be transcribed.

### Example Request

`Content-Type: multipart/form-data`

Form fields:

- `audio`: `<binary audio file>`

### Response: 200 OK

```json
{
  "transcript": "This is the transcribed audio."
}
```

#### Fields

- **transcript** `string`: Text transcription of the uploaded audio.

### Error Responses

- **400 Bad Request**

  ```json
  { "detail": "No audio data" }
  ```

- **502 Bad Gateway**

  ```json
  { "detail": "Transcription failed: <reason>" }
  ```

---

## Notes

- **Sessions are in-memory only**: If the backend restarts, all existing `session_id`s become invalid.
- **CORS**: All origins, methods, and headers are allowed in this MVP for ease of local development.
- **Automatic docs**: Since this is a FastAPI app, you can also access the auto-generated docs at:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

