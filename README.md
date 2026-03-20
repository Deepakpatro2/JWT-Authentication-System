# JWT Authentication System

A production-ready JWT-based authentication API built with **FastAPI** and **SQLAlchemy**.

---

## Features

- User Registration & Login
- Password hashing with **bcrypt**
- JWT Access Tokens (30 min) + Refresh Tokens (7 days)
- Refresh Token Rotation
- Protected Routes via Bearer token
- Server-side Logout (token revocation)
- Change Password
- Role-based access control foundation (`user` / `admin`)
- SQLite for development → swap to PostgreSQL for production

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn |
| ORM | SQLAlchemy |
| Database | SQLite / PostgreSQL |
| Password Hashing | passlib + bcrypt |
| JWT | python-jose |
| Validation | Pydantic v2 |
| Config | pydantic-settings + .env |

---

## Project Structure

```
Auth System/
├── app_v2.py               # Entry point
├── .env                    # Environment variables (do not commit)
├── .env.example            # Template for .env
├── requirements.txt
└── app/
    ├── core/
    │   ├── config.py       # Settings from .env
    │   └── security.py     # Password hashing + JWT utils
    ├── db/
    │   └── session.py      # DB engine + session
    ├── models/
    │   └── user.py         # User ORM model
    ├── schemas/
    │   └── auth.py         # Pydantic request/response schemas
    ├── services/
    │   └── auth_service.py # Business logic
    └── api/
        ├── auth.py         # Route handlers
        └── deps.py         # Auth dependencies
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Deepakpatro2/JWT-Authentication-System.git
cd JWT-Authentication-System
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

```bash
# Windows
venv\Scripts\Activate.ps1

# Mac / Linux
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Set up environment variables

```bash
# Copy the example file
cp .env.example .env
```

Open `.env` and update `SECRET_KEY`:

```
SECRET_KEY=your-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./auth.db
```

### 6. Run the server

```bash
uvicorn app_v2:app --reload
```

Server runs at: `http://127.0.0.1:8000`

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Create new account |
| POST | `/auth/login` | No | Login, get tokens |
| POST | `/auth/refresh` | No | Get new access token |
| GET | `/auth/profile` | Bearer | Protected user profile |
| POST | `/auth/logout` | Bearer | Revoke refresh token |
| POST | `/auth/change-password` | Bearer | Change password |
| GET | `/health` | No | Health check |

---

## Usage Examples

### Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Deepak Patro", "email": "deepak@example.com", "password": "secret123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "deepak@example.com", "password": "secret123"}'
```

### Access Protected Route

```bash
curl http://localhost:8000/auth/profile \
  -H "Authorization: Bearer <your_access_token>"
```

---

## Interactive API Docs

Once the server is running, open:

- **Swagger UI** → http://127.0.0.1:8000/docs
- **ReDoc** → http://127.0.0.1:8000/redoc

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing key — change in production | — |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `DATABASE_URL` | Database connection string | `sqlite:///./auth.db` |

---

## Production Notes

- Replace `SECRET_KEY` with a strong random value: `openssl rand -hex 32`
- Switch `DATABASE_URL` to PostgreSQL
- Set CORS `allow_origins` to your actual frontend domain
- Always serve over **HTTPS**
- Use **Alembic** for database migrations

---

## License

MIT
