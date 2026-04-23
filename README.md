# AI Email Workflow Automation System

FastAPI async backend for receiving emails, classifying them with an LLM, saving the structured analysis, and exposing the workflow through REST APIs.

## What It Does

- accepts incoming emails
- stores them in the database
- analyzes each email with Groq via LangChain
- classifies each email into one of 4 workflow categories:
  - `leave_request`
  - `support_issue`
  - `billing_issue`
  - `general_inquiry`
- assigns:
  - priority
  - recommended action
  - assigned team
  - human review flag
  - extracted structured entities
  - draft reply

## Tech Stack

- FastAPI
- SQLModel
- SQLAlchemy async
- PostgreSQL via `psycopg`
- Pydantic v2
- LangChain
- Groq
- Uvicorn

## Project Structure

```text
backend/
  app/
    api/v1/endpoints/      # REST endpoints
    core/                  # config and app exceptions
    db/                    # engine, session, init
    models/                # SQLModel database models
    schemas/               # request/response and AI schemas
    services/              # business logic and AI orchestration
    main.py                # FastAPI app entrypoint
  requirements.txt
```

## API Endpoints

Base prefix: `/api/v1`

- `GET /health`
- `POST /emails`
- `GET /emails`
- `GET /emails/{email_id}`
- `POST /emails/{email_id}/analyze`

## Environment Variables

Create `backend/.env` with:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB_NAME
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

Notes:

- `DATABASE_URL` must be an async SQLAlchemy-compatible connection string.
- `GROQ_MODEL` is optional because the app already defaults to `llama-3.1-8b-instant`.

## Local Setup

### 1. Create and activate a virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

The app will usually be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## How the Analysis Flow Works

1. Client creates an email with `POST /api/v1/emails`
2. Email is stored in the `emails` table
3. Client calls `POST /api/v1/emails/{email_id}/analyze`
4. Backend loads the email from the database
5. The analyzer sends the subject and body to the LLM
6. The LLM returns structured workflow data
7. Backend stores the result in `ai_email_analyses`
8. The original email status is updated to `analyzed`

## Example Request Flow

### Create an email

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/emails" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_email": "girish@gmail.com",
    "subject": "Unable to access my account after payment",
    "body": "Hi team. I completed the payment for my subscription this morning, but I still cannot access my account features. The payment was made from rahul.sharma@example.com and the amount was $49. Please check this issue and let me know what I need to do next. Thanks, Girish"
  }'
```

### Analyze that email

Replace `<email_id>` with the ID returned from the create step.

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/emails/<email_id>/analyze"
```

## Response Shape for Analysis

The analyze endpoint returns a structured payload similar to:

```json
{
  "id": "uuid",
  "email_id": "uuid",
  "category": "billing_issue",
  "priority": "high",
  "recommended_action": "create_billing_case",
  "assigned_team": "finance",
  "requires_human_review": false,
  "confidence": 0.92,
  "extracted_entities": {
    "customer_email_in_body": "rahul.sharma@example.com",
    "mentioned_amount": 49,
    "payment_method": "unknown",
    "affected_feature": "account features",
    "subscription_reference": null
  },
  "draft_reply": "Thank you for reaching out. We are checking the payment-related access issue and will update you shortly.",
  "analyzed_at": "2026-04-23T11:48:57.167931+00:00"
}
```

## Database Notes

- tables are created automatically on app startup
- `emails` stores the incoming message
- `ai_email_analyses` stores exactly one analysis per email

## Current Classification Rules

The analyzer currently routes emails into 4 categories:

- `leave_request`
- `support_issue`
- `billing_issue`
- `general_inquiry`

It uses a constrained prompt and structured output schema. This is good for straightforward emails, but it is still LLM-based and not foolproof for ambiguous or multi-intent emails.

## Common Dev Notes

- if an email was already analyzed once, analyzing it again will return a conflict
- if the email ID does not exist, the API returns `404`
- if AI analysis fails, the API returns `502`
- Swagger UI is available at `/docs`

## Future Improvements

- add labeled evaluation examples for each category
- add tests for category routing and edge cases
- improve ambiguity handling for multi-intent emails
- add request tracing or audit logging if needed later
