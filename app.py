import os
import uuid
import sqlite3
from datetime import datetime
from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google import genai

load_dotenv()

app = FastAPI(title="AI Chatbot")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chatbot.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

stop_flags = {}


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        original_name TEXT NOT NULL,
        stored_path TEXT NOT NULL,
        mime_type TEXT,
        uploaded_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'completed',
        attachment_id INTEGER,
        regenerated_from_id INTEGER,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (attachment_id) REFERENCES uploaded_files(id) ON DELETE SET NULL,
        FOREIGN KEY (regenerated_from_id) REFERENCES messages(id) ON DELETE SET NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        value TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_uploaded_files_session_id ON uploaded_files(session_id)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_preferences_key ON user_preferences(key)"
    )

    conn.commit()
    conn.close()


init_db()


def row_to_dict(row):
    return dict(row) if row else None


def get_preferences_dict():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM user_preferences ORDER BY key").fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}


def get_session_or_404(session_id: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM chat_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    return row


def update_session_timestamp(session_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now_iso(), session_id)
    )
    conn.commit()
    conn.close()


def add_message(
    session_id: int,
    role: str,
    content: str,
    status: str = "completed",
    attachment_id: Optional[int] = None,
    regenerated_from_id: Optional[int] = None,
):
    conn = get_conn()
    ts = now_iso()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO messages (session_id, role, content, timestamp, status, attachment_id, regenerated_from_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (session_id, role, content, ts, status, attachment_id, regenerated_from_id),
    )
    message_id = cur.lastrowid
    conn.execute(
        "UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (ts, session_id)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def get_messages_for_session(session_id: int):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT m.*, u.original_name, u.stored_path
        FROM messages m
        LEFT JOIN uploaded_files u ON m.attachment_id = u.id
        WHERE m.session_id = ?
        ORDER BY m.id ASC
    """,
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def build_prompt(
    session_id: int, user_message: str, attachment_text: Optional[str] = None
):
    preferences = get_preferences_dict()
    messages = get_messages_for_session(session_id)

    system_lines = [
        "You are a helpful AI assistant.",
        "Reply clearly and helpfully.",
        "If user preferences exist, follow them.",
    ]

    if preferences:
        system_lines.append("User preferences:")
        for k, v in preferences.items():
            system_lines.append(f"- {k}: {v}")

    tool_context = maybe_use_tool(user_message)
    if tool_context:
        system_lines.append("Tool result:")
        system_lines.append(tool_context)

    if attachment_text:
        system_lines.append("Attachment context:")
        system_lines.append(attachment_text)

    prompt_parts = ["\n".join(system_lines), "\nConversation history:"]
    for msg in messages[-12:]:
        prompt_parts.append(f"[{msg['role']}] {msg['content']}")

    prompt_parts.append(f"[user] {user_message}")
    return "\n".join(prompt_parts), tool_context


def maybe_use_tool(user_message: str) -> Optional[str]:
    text = user_message.strip()

    if text.lower().startswith("time:"):
        zone = text.split(":", 1)[1].strip() or "Asia/Taipei"
        try:
            resp = requests.get(
                f"https://worldtimeapi.org/api/timezone/{zone}", timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                dt = data.get("datetime", "unknown")
                tz = data.get("timezone", zone)
                return f"Current time in {tz} is {dt}."
            return f"Failed to fetch time for timezone {zone}."
        except Exception as e:
            return f"Time tool error: {str(e)}"

    return None


def call_gemini(prompt: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview", contents=prompt
    )
    if response.text:
        return response.text.strip()
    return "No response generated."


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/sessions")
async def list_sessions():
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM chat_sessions
        ORDER BY updated_at DESC, id DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/sessions")
async def create_session():
    conn = get_conn()
    ts = now_iso()
    title = f"New Chat {ts}"
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chat_sessions (title, created_at, updated_at)
        VALUES (?, ?, ?)
    """,
        (title, ts, ts),
    )
    session_id = cur.lastrowid
    conn.commit()
    row = conn.execute(
        "SELECT * FROM chat_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return dict(row)


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: int):
    get_session_or_404(session_id)
    return get_messages_for_session(session_id)


@app.post("/api/upload")
async def upload_file(session_id: int = Form(...), file: UploadFile = File(...)):
    get_session_or_404(session_id)

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    stored_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(stored_path, "wb") as f:
        content = await file.read()
        f.write(content)

    conn = get_conn()
    ts = now_iso()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO uploaded_files (session_id, original_name, stored_path, mime_type, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
    """,
        (session_id, file.filename, f"uploads/{unique_name}", file.content_type, ts),
    )
    file_id = cur.lastrowid
    conn.commit()
    row = conn.execute(
        "SELECT * FROM uploaded_files WHERE id = ?", (file_id,)
    ).fetchone()
    conn.close()

    update_session_timestamp(session_id)
    return dict(row)


@app.post("/api/chat")
async def chat(
    session_id: int = Form(...),
    message: str = Form(...),
    attachment_id: Optional[int] = Form(None),
):
    get_session_or_404(session_id)

    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    stop_flags[session_id] = False

    attachment_text = None
    if attachment_id:
        conn = get_conn()
        file_row = conn.execute(
            "SELECT * FROM uploaded_files WHERE id = ?", (attachment_id,)
        ).fetchone()
        conn.close()
        if file_row:
            attachment_text = (
                f"User attached a file.\n"
                f"Original name: {file_row['original_name']}\n"
                f"MIME type: {file_row['mime_type']}\n"
                f"Stored path: {file_row['stored_path']}"
            )

    user_msg = add_message(session_id, "user", message, attachment_id=attachment_id)

    try:
        if stop_flags.get(session_id):
            stopped_msg = add_message(
                session_id, "assistant", "Response stopped by user.", status="stopped"
            )
            return {"user_message": user_msg, "assistant_message": stopped_msg}

        prompt, tool_context = build_prompt(session_id, message, attachment_text)

        if stop_flags.get(session_id):
            stopped_msg = add_message(
                session_id, "assistant", "Response stopped by user.", status="stopped"
            )
            return {"user_message": user_msg, "assistant_message": stopped_msg}

        assistant_text = call_gemini(prompt)

        if stop_flags.get(session_id):
            stopped_msg = add_message(
                session_id, "assistant", "Response stopped by user.", status="stopped"
            )
            return {"user_message": user_msg, "assistant_message": stopped_msg}

        assistant_msg = add_message(
            session_id, "assistant", assistant_text, status="completed"
        )

        if tool_context:
            add_message(session_id, "tool", tool_context, status="completed")

        return {"user_message": user_msg, "assistant_message": assistant_msg}

    except Exception as e:
        error_msg = add_message(
            session_id, "assistant", f"Error: {str(e)}", status="error"
        )
        return JSONResponse(
            status_code=500,
            content={
                "user_message": user_msg,
                "assistant_message": error_msg,
                "detail": str(e),
            },
        )


@app.post("/api/messages/{message_id}/regenerate")
async def regenerate_message(message_id: int):
    conn = get_conn()
    original = conn.execute(
        "SELECT * FROM messages WHERE id = ?", (message_id,)
    ).fetchone()
    if not original:
        conn.close()
        raise HTTPException(status_code=404, detail="Message not found")

    session_id = original["session_id"]

    prev_user = conn.execute(
        """
        SELECT * FROM messages
        WHERE session_id = ? AND role = 'user' AND id < ?
        ORDER BY id DESC
        LIMIT 1
    """,
        (session_id, message_id),
    ).fetchone()
    conn.close()

    if not prev_user:
        raise HTTPException(
            status_code=400, detail="No previous user message found for regeneration"
        )

    try:
        prompt, _ = build_prompt(session_id, prev_user["content"])
        assistant_text = call_gemini(prompt)
        new_msg = add_message(
            session_id=session_id,
            role="assistant",
            content=assistant_text,
            status="completed",
            regenerated_from_id=message_id,
        )
        return new_msg
    except Exception as e:
        error_msg = add_message(
            session_id=session_id,
            role="assistant",
            content=f"Regenerate error: {str(e)}",
            status="error",
            regenerated_from_id=message_id,
        )
        return JSONResponse(status_code=500, content=error_msg)


@app.post("/api/stop")
async def stop_response(session_id: int = Form(...)):
    get_session_or_404(session_id)
    stop_flags[session_id] = True
    return {"success": True, "message": f"Stop requested for session {session_id}"}


@app.get("/api/preferences")
async def get_preferences():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM user_preferences ORDER BY key").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/preferences")
async def save_preferences(
    name: Optional[str] = Form(""),
    language: Optional[str] = Form(""),
    tone: Optional[str] = Form(""),
):
    prefs = {"name": name or "", "language": language or "", "tone": tone or ""}

    conn = get_conn()
    ts = now_iso()
    for key, value in prefs.items():
        existing = conn.execute(
            "SELECT * FROM user_preferences WHERE key = ?", (key,)
        ).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE user_preferences
                SET value = ?, updated_at = ?
                WHERE key = ?
            """,
                (value, ts, key),
            )
        else:
            conn.execute(
                """
                INSERT INTO user_preferences (key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """,
                (key, value, ts, ts),
            )
    conn.commit()
    rows = conn.execute("SELECT * FROM user_preferences ORDER BY key").fetchall()
    conn.close()
    return [dict(row) for row in rows]
