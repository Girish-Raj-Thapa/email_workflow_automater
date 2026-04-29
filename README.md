# AI Email Workflow Automation System

## Overview

This project is an AI-powered email automation platform that processes real incoming mail, classifies intent, routes work, drafts responses, and conditionally auto-sends safe replies.

It supports both:
- manual API-triggered processing (`POST /emails/process`)
- real mailbox ingestion via IMAP sync (`POST /operations/run-mail-sync` and background poll loop)

The pipeline is designed with explicit safety gates:
- prefiltering before AI
- category-based filtering after AI
- policy-based auto-send constraints

## Current Architecture

```text
Inbound Email Source
  - API submission
  - IMAP mailbox sync
      ↓
Pre-Filter (sender/keyword/quality/domain)
      ↓
Email Stored (audit trail)
      ↓
AI Analysis (LangChain + Groq + structured schema)
      ↓
Category Filter (allowlist)
      ↓
Workflow + Logs + Draft Reply
      ↓
Auto-Send Policy Check
  - pass -> SMTP send
  - fail -> keep draft for manual action
```

## Key Features Implemented

### 1. Real Mail Ingestion (IMAP)
- Polling-based mailbox sync with provider abstraction.
- Manual sync trigger endpoint: `POST /operations/run-mail-sync`.
- Deduplication by `(provider, provider_message_id)`.
- Stores source metadata (`source`, `provider`, `provider_message_id`, `thread_id`, `in_reply_to`).

### 2. Prefilter Before AI (Noise Control)
Incoming synced mail can be blocked before analysis using:
- blocked sender prefixes (`no-reply`, etc.)
- blocked keywords in subject/body (`newsletter`, `promo`, etc.)
- minimum body length
- max link count
- optional sender-domain allowlist

Blocked emails are still saved for audit with:
- `processing_status=ignored_prefilter`

### 3. AI Analysis with Structured Output
- Uses Groq model with strict schema constraints.
- Produces:
  - `category`
  - `priority`
  - `recommended_action`
  - `assigned_team`
  - `requires_human_review`
  - `confidence`
  - `extracted_entities`
  - `draft_reply`

### 4. Category-Based Post-Analysis Filter
Only categories in `MAIL_ALLOWED_CATEGORIES` continue to workflow/reply creation.

If blocked:
- analysis is stored
- `processing_status=ignored_category`
- no workflow/reply is created

### 5. Workflow Engine + Logs
- Creates workflow items with team/priority/status.
- Logs workflow lifecycle events.
- Supports status transitions via API.

### 6. Reply Lifecycle
- Draft replies are stored for each routable email.
- Manual send endpoint:
  - `POST /replies/{reply_id}/approve-and-send`
- Retry endpoint (failed only):
  - `POST /replies/{reply_id}/retry-send`

Reply tracking includes:
- `status` (`drafted`, `approved`, `queued`, `sent`, `failed`)
- `approved_by`
- `provider`, `provider_message_id`
- `sent_at`
- `error_message`
- `attempt_count`

### 7. Safe Auto-Send Policy (Phase 3)
Automatic sending runs only when all policy checks pass (see section below).

## Processing Status Values

Email records currently use these practical statuses:
- `received` (initial)
- `analyzed` (after AI analysis)
- `routed` (workflow/reply created)
- `ignored_prefilter` (blocked before AI)
- `ignored_category` (blocked after AI)

## Auto-Send Conditions

Auto-reply sending executes only if **all** are true:
1. `AUTO_SEND_ENABLED=true`
2. email is not prefiltered (`ignored_prefilter` path not triggered)
3. email passes category filter (`MAIL_ALLOWED_CATEGORIES`)
4. category is in `AUTO_SEND_SAFE_CATEGORIES`
5. priority is not `high`
6. `requires_human_review=false`
7. `confidence >= AUTO_SEND_MIN_CONFIDENCE`
8. reply exists and is in `drafted` state
9. SMTP send succeeds

If any check fails:
- reply remains draft for manual approval, or
- send attempt ends as `failed` with `error_message`.

## API Endpoints

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
- `POST /replies/{reply_id}/approve-and-send`
- `POST /replies/{reply_id}/retry-send`

### Operations
- `POST /operations/run-mail-sync`

## Tech Stack

### Backend
- FastAPI (async)
- SQLModel / SQLAlchemy
- PostgreSQL
- Alembic (migration workflow)

### AI
- LangChain
- Groq

### Frontend
- Streamlit

## Setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
# Core
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_email_workflow
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.1-8b-instant
DEBUG=true

# Inbound sync
MAIL_SYNC_ENABLED=true
MAIL_POLL_INTERVAL_SECONDS=60
MAIL_PROVIDER=imap
MAIL_ALLOWED_CATEGORIES=leave_request,support_issue,billing_issue,general_inquiry

IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your_email@gmail.com
IMAP_PASSWORD=your_app_password
IMAP_FOLDER=INBOX
IMAP_USE_SSL=true
IMAP_FETCH_LIMIT=20

# Prefilter
MAIL_ALLOWED_SENDER_DOMAINS=
MAIL_BLOCKED_SENDER_PREFIXES=no-reply,noreply,donotreply,mailer-daemon
MAIL_BLOCKED_SUBJECT_KEYWORDS=unsubscribe,newsletter,promo,security alert,welcome to
MAIL_MIN_BODY_LENGTH=40
MAIL_MAX_LINK_COUNT=15

# Outbound SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_ADDRESS=your_email@gmail.com
SMTP_USE_TLS=true

# Auto-send policy
AUTO_SEND_ENABLED=true
AUTO_SEND_SAFE_CATEGORIES=billing_issue,support_issue
AUTO_SEND_MIN_CONFIDENCE=0.85
```

Run API:

```bash
cd backend
make run
```

Swagger docs:
- `http://127.0.0.1:8000/docs`

### 2. Frontend

```bash
pip install streamlit requests
streamlit run frontend/app.py
```

## Migration Workflow (Alembic)

From `backend/`:

```bash
make revision m='describe_change'
make migrate
make current
make history
```

## End-to-End Runtime Behavior

### Manual processing (`POST /emails/process`)
1. saves email
2. runs AI analysis
3. applies category filter
4. creates workflow + draft reply if allowed
5. applies auto-send policy
6. either sends reply automatically or leaves draft

### Mail sync (`POST /operations/run-mail-sync`)
1. fetches IMAP messages
2. deduplicates provider message IDs
3. applies prefilter
4. stores blocked ones as `ignored_prefilter`
5. processes remaining through same analysis/workflow/reply/auto-send path

## Known Operational Notes

1. IMAP polling is interval-based; it is not webhook push yet.
2. AI classification can vary by phrasing; policy guards handle risk.
3. High-priority items are intentionally blocked from auto-send by default.
4. Use dedicated mailbox credentials for testing/automation workloads.

## Suggested Next Steps

1. Add Gmail push/webhook ingestion to reduce polling latency.
2. Store structured policy decision logs per email/reply for audit UI.
3. Add tenant/team-specific safe category and confidence thresholds.
4. Add retry backoff strategy for SMTP/network failures.
5. Add dashboard metrics:
   - prefilter skip rate
   - category-filter skip rate
   - auto-send pass/fail rate
   - manual queue volume

## License

MIT License
