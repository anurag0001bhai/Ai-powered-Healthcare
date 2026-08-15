"""
app.py
-------
Entry point for MindCare AI — an AI-based mental health monitoring app.
Handles login/signup and Gemini API key setup. Once logged in, users are
directed to use the pages in the sidebar (Chat, Journal, Mood Tracker,
Calorie Calculator, Dashboard).
"""

import streamlit as st
import database as db
import ai_utils

st.set_page_config(
    page_title="MindCare AI",
    page_icon="🧠",
    layout="centered",
)

db.init_db()

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "gemini_configured" not in st.session_state:
    st.session_state.gemini_configured = False


# ---------------------------------------------------------------------------
# Sidebar: API key input (kept out of source code for safety)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Setup")
    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get a free key at https://aistudio.google.com/apikey . "
             "Never commit your real key to source control.",
        value=st.session_state.get("gemini_api_key", ""),
    )
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input
        if not st.session_state.gemini_configured:
            ai_utils.configure_gemini(api_key_input)
            st.session_state.gemini_configured = True
        st.success("Gemini API key set ✅")
    else:
        st.info("Enter your Gemini API key to enable the chatbot.")

    st.divider()
    if st.session_state.user:
        st.write(f"👤 Logged in as **{st.session_state.user['username']}**")
        if st.button("Log out"):
            st.session_state.user = None
            st.rerun()


# ---------------------------------------------------------------------------
# Disclaimer (always visible)
# ---------------------------------------------------------------------------
st.title("🧠 MindCare AI")
st.caption("An AI-based mental health monitoring companion")

st.warning(
    "⚠️ **Disclaimer:** MindCare AI is a student/portfolio project and is "
    "**not** a substitute for professional mental health care. It cannot "
    "diagnose conditions or provide medical advice. If you are in crisis, "
    "please contact a local emergency service or helpline immediately."
)


# ---------------------------------------------------------------------------
# Login / Signup flow
# ---------------------------------------------------------------------------
if st.session_state.user is None:
    tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

    with tab_login:
        st.subheader("Log In")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In", type="primary"):
            user = db.verify_user(login_username, login_password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab_signup:
        st.subheader("Create an Account")
        new_username = st.text_input("Choose a username", key="signup_user")
        new_password = st.text_input("Choose a password", type="password", key="signup_pass")
        confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")
        if st.button("Sign Up", type="primary"):
            if not new_username or not new_password:
                st.error("Username and password can't be empty.")
            elif new_password != confirm_password:
                st.error("Passwords don't match.")
            elif len(new_password) < 4:
                st.error("Password should be at least 4 characters.")
            else:
                created = db.create_user(new_username, new_password)
                if created:
                    st.success("Account created! Please log in from the 'Log In' tab.")
                else:
                    st.error("That username is already taken.")

else:
    st.success(f"Welcome back, **{st.session_state.user['username']}**! 👋")
    st.markdown(
        """
        Use the sidebar to navigate:

        - **💬 Chat** — talk with your AI companion
        - **📓 Journal** — write and review journal entries
        - **📊 Mood Tracker** — log your daily mood and see trends
        - **🔥 Calorie Calculator** — find your maintenance, deficit & surplus targets
        - **🧭 Dashboard** — see your mood & sentiment trends together
        """
    )
