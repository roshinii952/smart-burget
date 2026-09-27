import json
import os
import sqlite3
from datetime import datetime
from hashlib import pbkdf2_hmac
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from services.gemini_utils import get_recommendations


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pocketsmart.db"
load_dotenv(BASE_DIR / ".env")


app = FastAPI(title="PocketSmart AI", version="1.0.0")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "dev-secret-change-me"),
    max_age=60 * 60 * 24 * 7,
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ============================================================
# DATABASE
# ============================================================

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()

    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )

    conn.execute(
        """CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            planner TEXT NOT NULL,
            input_json TEXT NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )"""
    )

    conn.commit()
    conn.close()


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        120000
    )

    return salt.hex() + ":" + digest.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":")

        digest = pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            120000
        )

        return digest.hex() == digest_hex

    except ValueError:
        return False


# ============================================================
# USER / SESSION
# ============================================================

def current_user(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    conn = db()

    user = conn.execute(
        "SELECT id, name, email FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    return dict(user) if user else None


def save_history(
    request: Request,
    planner: str,
    data: dict,
    result: dict
):
    user = current_user(request)

    if not user:
        return

    conn = db()

    conn.execute(
        """
        INSERT INTO history(
            user_id,
            planner,
            input_json,
            result_json,
            created_at
        )
        VALUES(?,?,?,?,?)
        """,
        (
            user["id"],
            planner,
            json.dumps(data),
            json.dumps(result),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    conn.commit()
    conn.close()


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
def startup():
    init_db()


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "user": current_user(request)
        }
    )


# ============================================================
# REGISTER
# ============================================================

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request,
            "user": current_user(request),
            "error": None
        }
    )


@app.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    name = name.strip()
    email = email.strip().lower()

    if len(password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "user": None,
                "error": "Password must be at least 6 characters."
            }
        )

    conn = db()

    try:
        cur = conn.execute(
            """
            INSERT INTO users(
                name,
                email,
                password_hash,
                created_at
            )
            VALUES(?,?,?,?)
            """,
            (
                name,
                email,
                hash_password(password),
                datetime.now().isoformat(timespec="seconds")
            ),
        )

        conn.commit()

        request.session["user_id"] = cur.lastrowid

    except sqlite3.IntegrityError:
        conn.close()

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "user": None,
                "error": "An account with that email already exists."
            }
        )

    conn.close()

    return RedirectResponse(
        "/dashboard",
        status_code=303
    )


# ============================================================
# LOGIN
# ============================================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "user": current_user(request),
            "error": None
        }
    )


@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    conn = db()

    user = conn.execute(
        "SELECT * FROM users WHERE email=?",
        (email.strip().lower(),)
    ).fetchone()

    conn.close()

    if not user or not verify_password(
        password,
        user["password_hash"]
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "user": None,
                "error": "Invalid email or password."
            }
        )

    request.session["user_id"] = user["id"]

    return RedirectResponse(
        "/dashboard",
        status_code=303
    )


# ============================================================
# LOGOUT
# ============================================================

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        "/",
        status_code=303
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = current_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=303
        )

    conn = db()

    rows = conn.execute(
        """
        SELECT planner, created_at
        FROM history
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 5
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "user": user,
            "recent": [dict(r) for r in rows]
        }
    )


# ============================================================
# HISTORY
# ============================================================

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    user = current_user(request)

    if not user:
        return RedirectResponse(
            "/login",
            status_code=303
        )

    conn = db()

    rows = conn.execute(
        """
        SELECT
            id,
            planner,
            input_json,
            result_json,
            created_at
        FROM history
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user["id"],)
    ).fetchall()

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "request": request,
            "user": user,
            "history": [dict(r) for r in rows]
        }
    )


# ============================================================
# HOME PLANNER
# ============================================================

@app.get("/home", response_class=HTMLResponse)
async def home_planner(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context={
            "request": request,
            "user": current_user(request),
            "planner": "home"
        }
    )


# ============================================================
# PARTY PLANNER
# ============================================================

@app.get("/party", response_class=HTMLResponse)
async def party_planner(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context={
            "request": request,
            "user": current_user(request),
            "planner": "party"
        }
    )


# ============================================================
# JEWELRY PLANNER
# ============================================================

@app.get("/jewelry", response_class=HTMLResponse)
async def jewelry_planner(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context={
            "request": request,
            "user": current_user(request),
            "planner": "jewelry"
        }
    )


# ============================================================
# RECOMMENDATION RESULT PAGE
# ============================================================

async def result_page(
    request: Request,
    planner: str,
    data: dict,
    image: UploadFile | None = None
):
    image_bytes = (
        await image.read()
        if image and image.filename
        else None
    )

    result = get_recommendations(
        planner,
        data,
        image_bytes,
        image.content_type if image else None
    )

    save_history(
        request,
        planner,
        data,
        result
    )

    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context={
            "request": request,
            "user": current_user(request),
            "planner": planner,
            "data": data,
            "result": result
        }
    )


# ============================================================
# GENERATE HOME RECOMMENDATIONS
# ============================================================

@app.post(
    "/generate-home",
    response_class=HTMLResponse
)
async def generate_home(
    request: Request,
    budget: float = Form(...),
    room_type: str = Form(...),
    lights: int = Form(0),
    fans: int = Form(0),
    tables: int = Form(0),
    style: str = Form("Modern"),
):
    data = {
        "budget": budget,
        "room_type": room_type,
        "lights": lights,
        "fans": fans,
        "tables": tables,
        "style": style
    }

    return await result_page(
        request,
        "home",
        data
    )


# ============================================================
# GENERATE PARTY RECOMMENDATIONS
# ============================================================

@app.post(
    "/generate-party",
    response_class=HTMLResponse
)
async def generate_party(
    request: Request,
    budget: float = Form(...),
    guests: int = Form(...),
    event_type: str = Form(...),
    venue: str = Form("Indoor"),
):
    data = {
        "budget": budget,
        "guests": guests,
        "event_type": event_type,
        "venue": venue
    }

    return await result_page(
        request,
        "party",
        data
    )


# ============================================================
# GENERATE JEWELRY RECOMMENDATIONS
# ============================================================

@app.post(
    "/generate-jewelry",
    response_class=HTMLResponse
)
async def generate_jewelry(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form(...),
    outfit_image: UploadFile | None = File(None),
):
    data = {
        "budget": budget,
        "occasion": occasion,
        "style": style,
        "image_uploaded": bool(
            outfit_image and outfit_image.filename
        )
    }

    return await result_page(
        request,
        "jewelry",
        data,
        outfit_image
    )


# ============================================================
# RECOMMENDATION DETAILS API
# ============================================================

@app.post("/recommendations-details")
async def recommendations_details(
    request: Request
):
    payload = await request.json()

    planner = payload.get(
        "planner",
        "home"
    )

    return JSONResponse(
        get_recommendations(
            planner,
            payload,
            None,
            None
        )
    )


# ============================================================
# SESSION INFO
# ============================================================

@app.get("/session-info")
async def session_info(request: Request):
    user = current_user(request)

    return {
        "logged_in": bool(user),
        "user_id": user["id"] if user else None,
        "name": user["name"] if user else None
    }


# ============================================================
# SESSION DATA
# ============================================================

@app.get("/session-data")
async def session_data(request: Request):
    user = current_user(request)

    if not user:
        return JSONResponse({
            "logged_in": False,
            "history_count": 0
        })

    conn = db()

    count = conn.execute(
        "SELECT COUNT(*) FROM history WHERE user_id=?",
        (user["id"],)
    ).fetchone()[0]

    conn.close()

    return {
        "logged_in": True,
        "user_id": user["id"],
        "history_count": count
    }


# ============================================================
# TOKEN
# ============================================================

@app.post("/token")
async def token(request: Request):
    user = current_user(request)

    if not user:
        return JSONResponse(
            {"error": "Login required"},
            status_code=401
        )

    return {
        "access_token": str(user["id"]),
        "token_type": "session"
    }


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )