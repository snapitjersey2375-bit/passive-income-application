# 🌌 Antigravity: The Autonomous Media Engine

**Antigravity** is a next-generation AI-driven media agency platform. It automates the entire content lifecycle—from deep-niche research and scriptwriting to animated video generation and multi-platform distribution.

---

## ✨ Features

- **🧠 Research Swarm**: Deep-dives into viral niches using LLM-powered synthesis.
- **🎬 AI Video Engine**: Generates high-impact HTML5 animations optimized for short-form video.
- **💸 Real Economy**: Integrated financial ledger with seed capital, ad budgets, and CPM-based revenue models.
- **🤝 Growth Loops**: Built-in referral system and waitlist management for viral scaling.
- **📡 Multi-Channel Publisher**: One-click manual or automatic publishing to TikTok and YouTube.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User((User)) -->|Dashboard| Web[Next.js Frontend]
    Web -->|REST API / JWT| Engine[FastAPI Backend]
    
    subgraph "The Hive (Agents)"
        Engine --> Researcher[Research Agent]
        Engine --> ContentSwarm[Content Swarm]
        Engine --> VideoGen[Video Generator]
        Engine --> Publisher[Publisher Agent]
    end
    
    subgraph "Persistence & External"
        Engine --> DB[(PostgreSQL / SQLite)]
        Researcher --> Search[Search APIs]
        Publisher --> Social[TikTok / YouTube]
    end
    
    Ledger[Ledger Service] --- Engine
    Ledger --- DB
```

---

## 🚀 Quick Start

### 1. Installation

Ensure you have Node.js 18+ and Python 3.10+ installed.

```bash
# Clone the repository
git clone https://github.com/your-repo/antigravity.git
cd antigravity

# Install monorepo dependencies
npm install
```

### 2. Environment Setup

Create a `.env` file in the root directory (refer to `.env.example`):

```bash
# Mandatory for AI features
OPENAI_API_KEY=sk-proj-...
ENCRYPTION_KEY=... # generate with fernet
SECRET_KEY=... # generate hex 32
```

### 3. Launch

```bash
# Start both frontend and backend in development mode
npm run dev
```

---

## 🚢 Production Deployment

### 📋 Production Readiness Checklist

Before deploying, ensure the following are completed:

- [x] **Secure Hashing**: Passwords use direct `bcrypt` hashing.
- [x] **JWT Auth**: Tokens are signed and verified in the backend.
- [x] **Frontend Security**: API calls include Bearer tokens; 401 errors trigger logout.
- [x] **Data Encryption**: Social platform tokens are encrypted in the DB.
- [x] **CORS**: Origins restricted via `ALLOWED_ORIGINS` env var.
- [x] **PostgreSQL**: Production database connected and migrations (or `Base.metadata.create_all`) run.

### 🔑 Environment Variables

#### Backend (`/apps/engine`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/db` |
| `SECRET_KEY` | Hex-encoded key for signing JWTs | `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | Fernet key for social tokens | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `OPENAI_API_KEY` | API key for research swarms | `sk-proj-...` |
| `ALLOWED_ORIGINS` | CORS allowlist (comma-separated) | `https://your-app.vercel.app` |

#### Frontend (`/apps/web`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | URL of your deployed backend | `https://api.your-app.railway.app` |

---

## 🏗️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14 (App Router), Tailwind CSS v4, Lucide Icons |
| **Backend** | FastAPI, Pydantic v2, Python 3.11 |
| **Database** | SQLAlchemy 2.0, PostgreSQL (Prod) / SQLite (Dev) |
| **Security** | JWT Authentication, Fernet Encryption for Social Tokens |
| **Ops** | Docker, Turbo (Monorepo), Railway (API), Vercel (Front) |

---

Detailed instructions for production setup can be found in the [walkthrough.md](.gemini/antigravity/brain/186bbada-d214-4943-ac2a-215ef61dfa9d/walkthrough.md).
