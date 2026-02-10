"""
Notification helpers for zakat alerts.
"""
import smtplib
from email.message import EmailMessage

from .config import get_secret


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def send_email_alert(subject, body):
    """
    Send an email alert with SMTP credentials from env/secrets.

    Required keys:
    - SMTP_HOST
    - SMTP_PORT
    - SMTP_USER
    - SMTP_PASS
    - ALERT_TO_EMAIL
    """
    smtp_host = get_secret("SMTP_HOST", "")
    smtp_port_raw = get_secret("SMTP_PORT", "587")
    smtp_user = get_secret("SMTP_USER", "")
    smtp_pass = get_secret("SMTP_PASS", "")
    to_email = get_secret("ALERT_TO_EMAIL", "")
    from_email = get_secret("ALERT_FROM_EMAIL", smtp_user)
    use_starttls = _as_bool(get_secret("SMTP_USE_STARTTLS", "true"), default=True)
    use_ssl = _as_bool(get_secret("SMTP_USE_SSL", "false"), default=False)

    missing = [
        key
        for key, value in {
            "SMTP_HOST": smtp_host,
            "SMTP_PORT": smtp_port_raw,
            "SMTP_USER": smtp_user,
            "SMTP_PASS": smtp_pass,
            "ALERT_TO_EMAIL": to_email,
        }.items()
        if not value
    ]
    if missing:
        return False, f"Missing email config: {', '.join(missing)}"

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        return False, f"Invalid SMTP_PORT: {smtp_port_raw}"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                if use_starttls:
                    server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        return True, f"Email sent to {to_email}"
    except Exception as exc:
        return False, f"SMTP send failed: {exc}"
