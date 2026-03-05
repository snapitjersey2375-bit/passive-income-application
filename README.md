# Antigravity Monorepo

Welcome to the Antigravity monorepo. This project consists of a Next.js frontend and a FastAPI backend engine designed for autonomous content curation and traffic generation.

## 🏗️ Architecture

- **`apps/web`**: Next.js 14+ frontend with Tailwind CSS v4.
- **`apps/engine`**: FastAPI backend implementing agents for research, content generation, and distribution.
- **`packages/ui`**: Shared UI component library.

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:

   ```bash
   npm install
   ```

2. **Environment Setup**:
   Copy `.env.example` to `.env` and fill in your keys:

   ```bash
   cp .env.example .env
   ```

3. **Run Dev Mode**:

   ```bash
   npm run dev
   ```

   - Web: [http://localhost:3000](http://localhost:3000)
   - Engine: [http://localhost:8000](http://localhost:8000)

### Docker

Build and run everything with Docker Compose:

```bash
docker-compose up --build
```

## 🚢 Deployment

### Backend (Railway)

1. Import the repo to Railway.
2. Set **Root Directory** to `apps/engine`.
3. Add a PostgreSQL database plugin.
4. Set required variables (`OPENAI_API_KEY`, `ALLOWED_ORIGINS`, etc.).

### Frontend (Vercel)

1. Import the repo to Vercel.
2. Set **Root Directory** to `apps/web`.
3. Set `NEXT_PUBLIC_API_URL` to your Railway URL.

## 🛠️ Tech Stack

- **Frontend**: Next.js, Tailwind v4, Turbo (Monorepo)
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Gunicorn
- **Agents**: LangChain-style patterns for Research & Distribution
