# 🛡 Domestic Violence Response System — Backend

A FastAPI backend for a domestic violence incident reporting and response system. Supports three roles — **Customer**, **Officer**, and **Admin** — with JWT authentication, AI-powered conversation analysis via Ollama, and a full test suite.

---

## 📁 Project Structure

```
Backend/
├── main.py                  # App entry point, router registration
├── models.py                # SQLAlchemy ORM models
├── settings.py              # App settings
├── seed.py                  # Database seeding script
│
├── db/
│   └── database.py          # DB engine, session, Base
│
├── routes/
│   ├── auth.py              # Signup & login (customer + officer)
│   ├── customer.py          # Customer profile, report, AI analyze
│   ├── officer.py           # Officer profile, incident management
│   └── admin.py             # Admin CRUD on all entities
│
├── utils/
│   ├── utils.py             # JWT create/decode helpers
│   └── deps.py              # Shared dependencies
│
├── unit_tests/
│   ├── test_auth.py         # Auth route tests
│   ├── test_cust.py         # Customer route tests
│   ├── test_off.py          # Officer route tests
│   └── test_admin.py        # Admin route tests
│
├── integration_tests/
│   ├── test_customer_flow.py
│   ├── test_officer_flow.py
│   └── test_admin_flow.py
│
├── system_tests/
│   ├── test_full_system.py
│   └── test_incident_lifecycle.py
│
├── run_tests.py             # Runs all tests in sequence
└── admin.html               # Admin dashboard UI
```

---

## 🗄 Database Models

### Customer
| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| username | String | Unique |
| email | String | Unique |
| password | String | Bcrypt hashed |
| phone | String | Unique, not null |
| address | String | Not null |

### Officer
| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| username | String | Unique |
| email | String | Unique |
| password | String | Bcrypt hashed |
| badge_number | String | Unique, not null |
| department | String | Not null |
| phone | String | Unique, not null |
| location | String | Not null |

### Incident
| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| customer_id | Integer | FK → customers |
| officer_id | Integer | FK → officers, nullable |
| description | Text | |
| location | String | |
| status | String | `initialized` / `assigned` / `resolved` |
| created_at | DateTime | Auto-set on creation |

---

## 🔐 Authentication

JWT-based auth using `python-jose`. Tokens carry `sub` (user ID) and `role` (`customer`, `officer`, or `admin`).

Admin credentials are hardcoded via `.env` — no DB table needed.

**Token is passed in the request body** for all protected routes:
```json
{ "token": "eyJhbGci..." }
```

---

## 🛣 API Routes

### Auth — `/auth`
| Method | Route | Description |
|---|---|---|
| POST | `/auth/signup` | Register as customer or officer |
| POST | `/auth/login` | Login, receive JWT |

### Customer — `/customer`
| Method | Route | Description |
|---|---|---|
| POST | `/customer/me` | Get own profile |
| PUT | `/customer/me` | Update email / phone / address |
| POST | `/customer/report` | File a manual incident report |
| POST | `/customer/analyze` | Submit conversation text for AI analysis |

### Officer — `/officer`
| Method | Route | Description |
|---|---|---|
| POST | `/officer/me` | Get own profile |
| PUT | `/officer/me` | Update email / phone / location / department |
| POST | `/officer/incidents/all` | View all unassigned incidents |
| POST | `/officer/incidents/accept` | Accept (claim) an incident |
| POST | `/officer/incidents` | View own assigned incidents |

### Admin — `/admin`
| Method | Route | Description |
|---|---|---|
| POST | `/admin/login` | Admin login |
| POST | `/admin/customers` | List all customers |
| PUT | `/admin/customers` | Edit a customer |
| POST | `/admin/officers` | List all officers |
| PUT | `/admin/officers` | Edit an officer |
| POST | `/admin/incidents` | List all incidents |
| PUT | `/admin/incidents` | Edit an incident (status, officer, description, location) |

---

## 🤖 AI Analysis

The `/customer/analyze` route accepts a conversation string and sends it to a locally running **Ollama** instance for domestic violence/aggression detection.

- Model: `gemma3:27b-cloud`
- Endpoint: `http://localhost:11434/api/chat`
- If flagged `True` → an incident is automatically created
- If flagged `False` → no action taken

Make sure Ollama is running before using this route:
```bash
ollama serve
```

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up `.env`
```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ADMIN_USERNAME=admin
ADMIN_PASSWORD=1234
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 3. Run the server
```bash
uvicorn main:app --reload
```

### 4. Seed the database (optional)
```bash
python seed.py
```

### 5. Open API docs
```
http://localhost:8000/docs
```

---

## 🧪 Running Tests

```bash
python run_tests.py
```

This runs all test files in order: **unit → integration → system**.

Or run individually:
```bash
python unit_tests/test_auth.py
python integration_tests/test_officer_flow.py
python system_tests/test_full_system.py
```

### Test Coverage Summary
| Suite | Files | What it tests |
|---|---|---|
| Unit | 4 files | Each route in isolation |
| Integration | 3 files | Cross-module flows |
| System | 2 files | Full end-to-end scenarios |

---

## 🖥 Admin Dashboard

Open `admin.html` directly in a browser. Login with the admin credentials from your `.env`.

Features:
- View all customers, officers, and incidents
- Edit any record inline via modal
- Assign officers to incidents
- Update incident status (`initialized` → `assigned` → `resolved`)
- Frontend validation on all fields (email format, 10-digit phone, required fields)
- Toast notifications on success/error

---

## 📊 Codebase Stats

| Category | Lines |
|---|---|
| Routes | ~566 |
| Tests | ~1,003 |
| Models / DB / Utils | ~155 |
| Config / Main | ~52 |
| **Total** | **~2,155** |

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | Web framework |
| SQLAlchemy | ORM |
| PostgreSQL | Database |
| bcrypt | Password hashing |
| python-jose | JWT tokens |
| Ollama (gemma3:4b) | Local AI model |
| python-dotenv | Environment config |
| requests | HTTP client (tests) |
