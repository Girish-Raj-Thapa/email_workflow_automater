# 📧 AI Email Workflow Automation System

## 🚀 Overview

This project is an AI-powered email workflow automation system that transforms unstructured email content into structured actions.

It automatically:

- analyzes incoming emails using an LLM
- classifies intent and priority
- routes tasks to the appropriate team
- creates workflow items (cases/tickets)
- generates draft replies
- tracks the workflow lifecycle with logs

The system demonstrates how modern applications can combine AI + backend workflows to automate real-world business processes like support handling, HR requests, and billing issues.

## ⚙️ Architecture

```text
Email Input
   ↓
AI Analysis (LangChain + Groq)
   ↓
Structured Output (Pydantic Schema)
   ↓
Workflow Engine
   ↓
Workflow Item + Logs
   ↓
Draft Reply Generation
```

## 🧠 Core Features

### 1. Email Processing

- Submit emails via API or Streamlit UI
- Stores email with processing status (`received` → `analyzed` → `routed`)

### 2. AI Analysis

- Uses LangChain + Groq (default model: `llama-3.1-8b-instant`)
- Converts email text into structured data:
  - `category`
  - `priority`
  - `assigned_team`
  - `recommended_action`
  - `extracted_entities`
  - `draft_reply`

### 3. Workflow Engine

- Automatically creates workflow items based on AI output
- Assigns:
  - team (`hr` / `technical_support` / `finance` / `manual_review`)
  - priority (`low` / `medium` / `high`)
  - status (`open` / `escalated` / `awaiting_review`)

### 4. Workflow Tracking

- Logs every step:
  - workflow creation
  - assignment
  - priority setting
  - escalation
  - status updates

### 5. Status Management

- Update workflow status via API or UI
- Full lifecycle tracking supported:
  - `open` → `in_progress` → `resolved` → `closed`
- Additional states:
  - `awaiting_review`
  - `escalated`

### 6. Reply Generation

- Automatically generates a draft reply for each email
- Stored and viewable via API/UI

### 7. Debug Trace Utility (Dev)

- Includes a trace utility at `backend/debug_traces/debug_trace.py` for detailed run logging
- Trace file path: `backend/debug_traces/analyze_trace.log`
- Dev behavior is controlled from `.env` (`DEBUG=true/false`)

## 🖥️ Frontend (Streamlit)

Minimal UI built using Streamlit:

- 📥 Process Email
- 📬 Inbox
- 🧩 Workflows (with status update + logs)
- ✉️ Replies

## 🧱 Tech Stack

### Backend

- FastAPI (async)
- SQLModel / SQLAlchemy
- PostgreSQL

### AI Layer

- LangChain
- Groq (LLaMA / Mixtral-compatible models)

### Frontend

- Streamlit

### Others

- Pydantic
- Requests

## 📡 API Endpoints

Base prefix: `/api/v1`

### Health

- `GET /health`

### Emails

- `POST /emails`
- `POST /emails/process`
- `GET /emails`
- `GET /emails/{email_id}`

### AI Analysis

- `POST /emails/{email_id}/analyze`

### Workflows

- `GET /workflows`
- `GET /workflows/{workflow_id}`
- `PATCH /workflows/{workflow_id}/status`

### Replies

- `GET /replies`
- `GET /replies/{reply_id}`

## 🔄 Example Flow

`POST /api/v1/emails/process`

- Email saved
- AI analyzes email
- Workflow created
- Team assigned
- Status set (`open` / `escalated` / `awaiting_review`)
- Draft reply generated
- Response returned

## 🛠️ Setup Instructions

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_email_workflow
GROQ_API_KEY=your_key
GROQ_MODEL=llama-3.1-8b-instant
DEBUG=true
```

Run server:

```bash
uvicorn app.main:app --reload
```

API docs:

- `http://127.0.0.1:8000/docs`

### 2. Frontend

```bash
pip install streamlit requests
streamlit run frontend/app.py
```

## 📸 Screenshots

Add project screenshots for:

- Process Email page
- Inbox
- Workflows with logs
- Replies
- Swagger UI

## 📌 Future Improvements

- Real email integration (IMAP / Gmail API)
- Background processing (Celery / Redis)
- Multi-step agent workflows
- Authentication & roles
- Production deployment

## 💡 Key Learning

This project demonstrates:

- how to integrate LLMs into backend systems
- how to enforce structured output from AI
- how to design workflow engines
- how to automate real-world processes using AI

## 🧾 License

MIT License
