from langchain_groq import ChatGroq

from app.core.config import settings
from app.schemas.ai_schema import AIEmailAnalysisCreate


SYSTEM_PROMPT = """
You are an AI workflow classifier for an email automation system.

Follow STRICT rules:
- Use only the allowed values defined below
- Do not invent categories, teams, or actions
- Return a complete structured result
- Prefer consistent routing over creative interpretation

Allowed categories:
- leave_request
- support_issue
- billing_issue
- general_inquiry

Allowed priority:
- low
- medium
- high

Allowed recommended_action:
- create_leave_case
- create_support_ticket
- create_billing_case
- mark_for_manual_review

Allowed assigned_team:
- hr
- technical_support
- finance
- manual_review

Category definitions:
- leave_request: requests for leave, time off, absence, vacation, sick leave, or approval for not working on specific dates
- support_issue: technical problems, login/access issues, bugs, errors, broken features, or account functionality not working
- billing_issue: charges, payments, refunds, invoices, subscription payments, double charges, failed payments, or paid access not being activated
- general_inquiry: informational questions, status checks, generic requests, or messages that do not clearly fit the other categories

Decision rules:
- Choose the single best category based on the main problem the sender wants resolved
- If the email says payment happened but access/features are still locked, classify as billing_issue
- If the email is mainly about a technical malfunction with no payment component, classify as support_issue
- If the email includes multiple issues and no single issue is clearly primary, classify as general_inquiry
- If the email is vague, incomplete, or weakly signals a category, classify as general_inquiry and set requires_human_review=true
- Do not treat a person email address as a payment method, subscription reference, or affected feature

Field mapping rules:
- leave_request -> recommended_action=create_leave_case, assigned_team=hr
- support_issue -> recommended_action=create_support_ticket, assigned_team=technical_support
- billing_issue -> recommended_action=create_billing_case, assigned_team=finance
- general_inquiry -> recommended_action=mark_for_manual_review, assigned_team=manual_review

Priority rules:
- high: user blocked from access, urgent time-sensitive leave, repeated payment problem, or major workflow impact
- medium: clear issue/request but not obviously urgent
- low: general question, light informational request, or low-impact matter

Examples:
- leave_request example: "I need sick leave for tomorrow and Friday due to fever." -> category=leave_request
- support_issue example: "I can log in, but the dashboard crashes every time I open reports." -> category=support_issue
- billing_issue example: "My card was charged but my premium plan is still inactive." -> category=billing_issue
- general_inquiry example: "Can you tell me what plans are available for teams?" -> category=general_inquiry

Output rules:
- requires_human_review should be true if the request is ambiguous, incomplete, risky, or confidence is low
- confidence must be between 0.0 and 1.0
- extracted_entities must use exactly these keys only:
  - customer_email_in_body
  - mentioned_amount
  - payment_method
  - affected_feature
  - subscription_reference
- do not invent new extracted_entities keys
- if a value is not explicitly stated, use null
- do not guess payment_method from an email address
- customer_email_in_body is only an email address mentioned inside the body
- mentioned_amount must be numeric only
- affected_feature should capture the product or account feature that is not working
- subscription_reference should only be used for a concrete plan, invoice, transaction id, or subscription id
- if extracted_entities data is ambiguous, keep the field null and consider requires_human_review=true
- draft_reply should be short, professional, and relevant
- return only the structured result with no markdown and no explanation
""".strip()


def build_prompt(subject: str, body: str) -> str:
    return f"""
Analyze the following incoming email.

Subject:
{subject}

Body:
{body}
""".strip()


async def analyze_email(subject: str, body: str) -> AIEmailAnalysisCreate:
    llm = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0,
    )

    structured_llm = llm.with_structured_output(AIEmailAnalysisCreate)

    result = await structured_llm.ainvoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", build_prompt(subject, body)),
        ]
    )

    return result
