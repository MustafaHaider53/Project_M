import streamlit as st


def apply_islamic_theme() -> None:
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400;1,700&family=Noto+Naskh+Arabic:wght@400..700&display=swap');

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

          /* Hide default Streamlit header and footer completely */
          header[data-testid="stHeader"] {
            display: none !important;
          }
          footer {
            display: none !important;
          }

          /* Remove borders, shadows, and backgrounds around the main app container and layout wrappers */
          .stAppViewContainer {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          [data-testid="stAppViewContainer"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          .stMain {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          [data-testid="stMain"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          .stMainBlockContainer {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          [data-testid="stMainBlockContainer"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
            padding: 0.5rem 1rem 1rem 1rem !important;
            max-width: 100% !important;
          }
          .block-container {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
            padding: 0.5rem 1rem 1rem 1rem !important;
            max-width: 100% !important;
          }
          .main {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          .stApp > div {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          div[data-testid="stVerticalBlockBorderOnly"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"] > div {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
          }

          /* Style for mistake cards (Hifz, Ahkam, Makharij) */
          div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid var(--border) !important;
            background: var(--card) !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 12px rgba(30,26,18,0.03) !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"] > div {
            border: none !important;
            background: transparent !important;
            padding: 6px 8px !important;
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

          /* Tighten vertical layout gaps */
          div[data-testid="column"] div[data-testid="stVerticalBlock"] {
            gap: 4px !important;
          }

          /* Buttons */
          .stButton, div[data-testid="stFormSubmitButton"] {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
          }
          .stButton > button, div[data-testid="stFormSubmitButton"] > button {
            width: 100% !important;
            padding: 2px 4px !important;
            font-size: 10px !important;
            height: 26px !important;
            min-height: 26px !important;
            line-height: 1.2 !important;
            border-radius: 8px !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            border: 1px solid var(--border) !important;
            background: linear-gradient(180deg, rgba(212,175,55,0.28), rgba(212,175,55,0.14)) !important;
            color: var(--ink) !important;
            font-weight: 600 !important;
          }
          .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
            border-color: rgba(212,175,55,0.55) !important;
            background: linear-gradient(180deg, rgba(212,175,55,0.38), rgba(212,175,55,0.18)) !important;
          }

          /* Primary button (Streamlit applies different classes; this catches most cases) */
          .stButton > button[kind="primary"],
          div[data-testid="stFormSubmitButton"] > button[kind="primary"],
          .stButton > button:has(span[data-testid="stText"]),
          div[data-testid="stFormSubmitButton"] > button:has(span[data-testid="stText"]) {
            box-shadow: 0 10px 30px rgba(212,175,55,0.10);
          }

          /* Inputs */
          [data-baseweb="select"] > div,
          div[data-baseweb="input"],
          .stTextArea textarea {
            border-radius: 12px !important;
            border: 1.5px solid var(--border) !important;
            background: rgba(255, 255, 255, 0.85) !important;
            color: var(--ink) !important;
            transition: all 0.2s ease-in-out !important;
          }

          /* Ensure all inner elements of inputs are transparent and borderless */
          div[data-baseweb="input"] * {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
          }

          /* Focus state for inputs */
          div[data-baseweb="input"]:focus-within,
          [data-baseweb="select"] > div:focus-within,
          .stTextArea textarea:focus {
            border-color: var(--emerald) !important;
            box-shadow: 0 0 0 1px var(--emerald) !important;
            background: #ffffff !important;
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
            margin: 4px 0 !important;
          }

          /* Sticky Header Container (only targets the inner container wrapping sticky elements) */
          div[data-testid="stVerticalBlock"]:has(> div > div > .sticky-anchor) {
            position: -webkit-sticky;
            position: sticky;
            top: 0px;
            z-index: 999;
            background: var(--bg) !important;
            border-bottom: 2px solid var(--border) !important;
            padding: 4px 12px !important;
            box-shadow: 0 10px 30px rgba(30,26,18,0.08) !important;
            border-radius: 0 0 16px 16px !important;
          }

          /* Compact Buttons inside the sticky container to fit mobile screens */
          div[data-testid="stVerticalBlock"]:has(> div > div > .sticky-anchor) .stButton > button {
            padding: 0.35rem 0.6rem !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            line-height: 1.2 !important;
            height: auto !important;
          }

          /* Target 3-column rows (button + label + button) on desktop to align them symmetrically */
          div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            justify-content: space-between !important;
            align-items: center !important;
            gap: 4px !important;
            width: 100% !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(1),
          div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(3) {
            flex: 0 0 26px !important;
            width: 26px !important;
            max-width: 26px !important;
            min-width: 26px !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(2) {
            flex: 1 1 0% !important;
            min-width: 0 !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) .stButton > button {
            width: 26px !important;
            max-width: 26px !important;
            height: 26px !important;
            min-height: 26px !important;
            padding: 0 !important;
            font-size: 13px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
          }

          /* Clear Arabic fonts on Makharij buttons (using card anchor) */
          div[data-testid="stVerticalBlockBorderWrapper"]:has(.makharij-card-anchor) .stButton > button,
          div[data-testid="stVerticalBlockBorderWrapper"]:has(.makharij-card-anchor) .stButton > button * {
            font-family: 'Amiri', 'Noto Naskh Arabic', 'Simplified Arabic', 'Traditional Arabic', 'Arabic Typesetting', serif !important;
            font-size: 15.5px !important;
            font-weight: 700 !important;
            overflow: visible !important;
            line-height: 0.9 !important;
            padding: 0 !important;
            margin: 0 !important;
          }

          /* Active green styling for Makharij letter buttons */
          div[data-testid="stElementContainer"]:has(.makhraj-active) + div[data-testid="stElementContainer"] button,
          div[data-testid="stElementContainer"]:has(.makhraj-active) ~ div[data-testid="stElementContainer"] button {
            background: linear-gradient(180deg, #15803d, #166534) !important;
            color: #ffffff !important;
            border-color: #14532d !important;
          }
          div[data-testid="stElementContainer"]:has(.makhraj-active) + div[data-testid="stElementContainer"] button:hover,
          div[data-testid="stElementContainer"]:has(.makhraj-active) ~ div[data-testid="stElementContainer"] button:hover {
            background: linear-gradient(180deg, #166534, #14532d) !important;
          }

          /* Mobile responsive layout overrides to prevent vertical column stacking and scrolling */
          @media (max-width: 991px) {
            .block-container {
              padding: 0.5rem 0.15rem 0.25rem 0.15rem !important;
            }

            /* Tighten vertical layout gaps on mobile */
            div[data-testid="column"] div[data-testid="stVerticalBlock"] {
              gap: 3px !important;
            }

            /* 1. Force nested mistake columns (horizontal blocks) to stay in a row on mobile */
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"] {
              display: flex !important;
              flex-direction: row !important;
              flex-wrap: nowrap !important;
              gap: 4px !important;
              margin-bottom: 2px !important;
              align-items: center !important;
            }

            /* 2. Force nested columns inside mistake cards to shrink appropriately without overflowing */
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="column"] {
              min-width: 0 !important;
              flex: 1 1 0% !important;
              padding: 0 !important;
            }

            /* Allow navigation row (7 columns) to wrap on mobile so buttons do not overlap */
            div[data-testid="stHorizontalBlock"]:not(div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]):has(div[data-testid="column"]:nth-child(7)) {
              flex-wrap: wrap !important;
              gap: 5px 3px !important;
            }
            div[data-testid="stHorizontalBlock"]:not(div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]):has(div[data-testid="column"]:nth-child(7)) div[data-testid="column"] {
              flex: 1 1 28% !important;
              min-width: 80px !important;
            }

            /* Symmetrical 3-column mistake rows on mobile */
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(1),
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(3) {
              flex: 0 0 23px !important;
              width: 23px !important;
              max-width: 23px !important;
              min-width: 23px !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(2) {
              flex: 1 1 0% !important;
              min-width: 0 !important;
            }

            /* 3. Make ALL buttons very compact and prevent overlapping via ellipsis truncation */
            .stButton, div[data-testid="stFormSubmitButton"] {
              border: none !important;
              background: transparent !important;
              box-shadow: none !important;
              padding: 0 !important;
              margin: 0 !important;
            }
            .stButton > button, div[data-testid="stFormSubmitButton"] > button {
              width: 100% !important;
              padding: 2px 1px !important;
              font-size: 8.5px !important;
              height: 23px !important;
              min-height: 23px !important;
              line-height: 1.1 !important;
              border-radius: 6px !important;
              text-overflow: ellipsis !important;
              white-space: nowrap !important;
              overflow: hidden !important;
              display: flex !important;
              align-items: center !important;
              justify-content: center !important;
              margin: 0 !important;
            }

            /* Override the global button style for emoji buttons to keep them square on mobile */
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) .stButton > button {
              width: 23px !important;
              max-width: 23px !important;
              height: 23px !important;
              min-height: 23px !important;
              padding: 0 !important;
              font-size: 11px !important;
            }

            /* Makharij Arabic font sizing overrides for mobile (using card anchor) */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.makharij-card-anchor) .stButton > button,
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.makharij-card-anchor) .stButton > button * {
              font-family: 'Amiri', 'Noto Naskh Arabic', 'Simplified Arabic', 'Traditional Arabic', 'Arabic Typesetting', serif !important;
              font-size: 12.5px !important;
              font-weight: 700 !important;
              overflow: visible !important;
              line-height: 0.9 !important;
              padding: 0 !important;
              margin: 0 !important;
            }

            /* Adjust titles and texts */
            h3 {
              font-size: 0.95rem !important;
              margin: 0 !important;
            }
            div[data-testid="stVerticalBlock"] p,
            div[data-testid="stVerticalBlock"] span,
            div[data-testid="stVerticalBlock"] div {
              font-size: 11px !important;
            }
            hr {
              margin: 0.4rem 0 !important;
            }
          }

          /* Float selectbox popover dropdowns to top of screen on short/landscape mobile view to avoid keyboard overlaps */
          @media (max-height: 480px) {
            div[data-baseweb="popover"] {
              position: fixed !important;
              top: 8px !important;
              left: 12px !important;
              right: 12px !important;
              width: auto !important;
              bottom: auto !important;
              transform: none !important;
              z-index: 999999 !important;
              box-shadow: 0 10px 30px rgba(30,26,18,0.25) !important;
            }
            /* Reset Popper.js dynamic translate3d/top offsets on the child wrapper */
            div[data-baseweb="popover"] > div {
              transform: none !important;
              top: 0 !important;
              left: 0 !important;
              right: 0 !important;
              position: relative !important;
            }
            div[data-baseweb="menu"] {
              max-height: 120px !important;
              overflow-y: auto !important;
              border: 2px solid var(--gold) !important;
              border-radius: 10px !important;
              background-color: rgba(255, 255, 255, 0.98) !important;
            }
            div[data-baseweb="menu"] ul {
              max-height: 120px !important;
              overflow-y: auto !important;
            }
          }

          /* Hide background communication iframe completely */
          iframe[height="1"], 
          iframe[style*="height: 1px"],
          div[data-testid="stIframe"]:has(iframe[height="1"]),
          div[data-testid="stIframe"]:has(iframe[style*="height: 1px"]) {
            display: none !important;
            height: 0 !important;
            width: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
            margin: 0 !important;
            padding: 0 !important;
            position: absolute !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

