import streamlit as st


def apply_islamic_theme() -> None:
    st.markdown(
        """
        <style>
          :root{
            --gold: #D4AF37;
            --gold-2: #B88917;
            --emerald: #0E6B50;
            --ink: #1E1A12;
            --bg: #FBF6EA;
            --bg-2: #F3E9D2;
            --card: rgba(212,175,55,0.10);
            --border: rgba(184,137,23,0.35);
          }

          /* Main container */
          .stApp {
            background: radial-gradient(1200px 600px at 20% -10%, rgba(212,175,55,0.22), transparent 60%),
                        radial-gradient(900px 500px at 100% 0%, rgba(14,107,80,0.14), transparent 55%),
                        linear-gradient(180deg, var(--bg), var(--bg-2) 75%);
          }

          /* Title */
          h1, h2, h3 {
            letter-spacing: 0.2px;
          }
          h1 {
            color: var(--ink);
          }

          /* Cards / expanders */
          [data-testid="stExpander"] > details {
            border: 1px solid var(--border) !important;
            background: var(--card) !important;
            border-radius: 14px !important;
          }

          /* Buttons */
          .stButton > button {
            border-radius: 14px !important;
            border: 1px solid var(--border) !important;
            background: linear-gradient(180deg, rgba(212,175,55,0.28), rgba(212,175,55,0.14)) !important;
            color: var(--ink) !important;
            font-weight: 650 !important;
            padding: 0.7rem 1rem !important;
          }
          .stButton > button:hover {
            border-color: rgba(212,175,55,0.55) !important;
            background: linear-gradient(180deg, rgba(212,175,55,0.38), rgba(212,175,55,0.18)) !important;
          }

          /* Primary button (Streamlit applies different classes; this catches most cases) */
          .stButton > button[kind="primary"],
          .stButton > button:has(span[data-testid="stText"]) {
            box-shadow: 0 10px 30px rgba(212,175,55,0.10);
          }

          /* Inputs */
          [data-baseweb="select"] > div,
          .stTextInput input,
          .stNumberInput input,
          .stTextArea textarea {
            border-radius: 12px !important;
            border: 1.5px solid var(--border) !important;
            background: rgba(255, 255, 255, 0.85) !important;
            color: var(--ink) !important;
          }

          /* Dataframe / editor container */
          [data-testid="stDataFrame"],
          [data-testid="stDataEditor"] {
            border: 1px solid rgba(212,175,55,0.22) !important;
            border-radius: 14px !important;
            overflow: hidden !important;
          }

          /* Caption emphasis */
          .stCaption, [data-testid="stCaptionContainer"] {
            color: rgba(30,26,18,0.70) !important;
          }

          /* Subtle divider */
          hr {
            border-color: rgba(212,175,55,0.18) !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

