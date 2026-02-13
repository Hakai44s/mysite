"""
Authentication helpers for Streamlit pages.
"""
import hmac
import os
import streamlit as st


def _read_dotenv_value(key):
    """Read a simple key=value from .env for local execution."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(project_root, ".env")
    if not os.path.exists(dotenv_path):
        return ""

    with open(dotenv_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            env_key, env_value = line.split("=", 1)
            if env_key.strip() != key:
                continue
            return env_value.strip().strip('"').strip("'")
    return ""


def _get_app_password():
    """Priority: st.secrets -> env var -> .env file."""
    secret_value = ""
    try:
        secret_value = st.secrets.get("APP_PASSWORD", "")
    except Exception:
        pass
    if secret_value:
        return str(secret_value)

    env_value = os.getenv("APP_PASSWORD", "")
    if env_value:
        return env_value

    return _read_dotenv_value("APP_PASSWORD")


def require_password():
    """Block app/page until password is correct."""
    app_password = _get_app_password()
    if not app_password:
        st.error(
            "APP_PASSWORD non configure. Ajoute APP_PASSWORD dans Streamlit Secrets (cloud) "
            "ou dans .env (local)."
        )
        st.stop()

    if st.session_state.get("auth_ok", False):
        return

    st.markdown("## Acces protege")
    with st.form("password_form", clear_on_submit=False):
        entered_password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Entrer")
    if submitted:
        if hmac.compare_digest(entered_password, app_password):
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()
