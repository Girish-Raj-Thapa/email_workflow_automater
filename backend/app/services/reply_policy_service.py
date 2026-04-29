from dataclasses import dataclass

from app.core.config import settings
from app.models.ai_analysis import AIEmailAnalysis
from app.models.reply import SentReply


@dataclass
class PolicyDecision:
    allow_auto_send: bool 
    reason: str


def should_auto_send_reply(
    analysis: AIEmailAnalysis,
    reply: SentReply,
) -> PolicyDecision:
    if not settings.auto_send_enabled:
        return PolicyDecision(False, "auto_send_disabled")

    category = (analysis.category or "").strip().lower()
    if category not in settings.auto_send_safe_categories_set:
        return PolicyDecision(False, f"category_not_safe:{category}")

    if analysis.priority == "high":
        return PolicyDecision(False, "high_priority_block")

    if analysis.requires_human_review:
        return PolicyDecision(False, "human_review_required")

    if analysis.confidence < settings.auto_send_min_confidence:
        return PolicyDecision(False, "low_confidence")

    if reply.status != "drafted":
        return PolicyDecision(False, f"reply_status_not_drafted:{reply.status}")

    return PolicyDecision(True, "policy_pass")


