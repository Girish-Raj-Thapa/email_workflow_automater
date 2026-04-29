from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Email Workflow Automation System"
    app_version: str = "0.1.0"
    debug: bool = True
    database_url: str

    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"

    # Mail sync settings
    mail_sync_enabled: bool = False
    mail_poll_interval_seconds: int = 60
    mail_provider: str = "imap"

    # IMAP settings
    imap_host: str = ""
    imap_port: int = 993
    imap_username: str = ""
    imap_password: str = ""
    imap_folder: str = "INBOX"
    imap_use_ssl: bool = True
    imap_fetch_limit: int = 20

    # SMTP settings
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_address: str = ""
    smtp_use_tls: bool = True

    # Category filter settings
    mail_allowed_categories: str = (
        "leave_request,support_issue,billing_issue,general_inquiry"
    )  

    auto_send_enabled: bool = False 
    auto_send_safe_categories: str = "billing_issue,support_issue"
    auto_send_min_confidence: float = 0.85

    @property
    def auto_send_safe_categories_set(self) -> set[str]:
        return self._csv_to_set(self.auto_send_safe_categories)

    @property
    def allowed_categories_set(self) -> set[str]:
        return {
            item.strip().lower()
            for item in self.mail_allowed_categories.split(",")
            if item.strip()
        }

    # Pre-filter settings
    mail_allowed_sender_domains: str = ""
    mail_blocked_sender_prefixes: str = "no-reply,noreply,donotreply,mailer-daemon"
    mail_blocked_subject_keywords: str = "unsubscribe,newsletter,promo,security alert,welcome to"
    mail_min_body_length: int = 40
    mail_max_link_count: int = 15

    @staticmethod
    def _csv_to_set(value: str) -> set[str]:
        return {item.strip().lower() for item in value.split(",") if item.strip()}

    @property
    def allowed_sender_domains_set(self) -> set[str]:
        return self._csv_to_set(self.mail_allowed_sender_domains)

    @property
    def blocked_sender_prefixes_set(self) -> set[str]:
        return self._csv_to_set(self.mail_blocked_sender_prefixes)

    @property
    def blocked_subject_keywords_set(self) -> set[str]:
        return self._csv_to_set(self.mail_blocked_subject_keywords)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
