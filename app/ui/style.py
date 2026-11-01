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

          /* Target 3-column rows (button + label + button) inside Hifz card on desktop to align them symmetrically */
          div[data-testid="stVerticalBlockBorderWrapper"]:has(.hifz-card-anchor) div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            justify-content: space-between !important;
            align-items: center !important;
            gap: 4px !important;
            width: 100% !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"]:has(.hifz-card-anchor) div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(1),
          div[data-testid="stVerticalBlockBorderWrapper"]:has(.hifz-card-anchor) div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(3) {
            flex: 0 0 26px !important;
            width: 26px !important;
            max-width: 26px !important;
            min-width: 26px !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"]:has(.hifz-card-anchor) div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) div[data-testid="column"]:nth-child(2) {
            flex: 1 1 0% !important;
            min-width: 0 !important;
          }
          div[data-testid="stVerticalBlockBorderWrapper"]:has(.hifz-card-anchor) div[data-testid="stHorizontalBlock"]:has(div[data-testid="column"]:nth-child(3)) .stButton > button {
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

          /* Compact sizing for Ahkam Tajweed buttons to match Hifz & Makharij card height */
          div[data-testid="stVerticalBlockBorderWrapper"]:has(.ahkam-card-anchor) .stButton > button {
            padding: 0.2rem 0.15rem !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
            line-height: 1.15 !important;
            min-height: 26px !important;
            height: 26px !important;
            overflow: hidden !important;
            white-space: nowrap !important;
            text-overflow: ellipsis !important;
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

          /* Active green styling for Makharij letter and Ahkam Tajweed buttons */
          div[data-testid="stElementContainer"]:has(.makhraj-active) + div[data-testid="stElementContainer"] button,
          div[data-testid="stElementContainer"]:has(.makhraj-active) ~ div[data-testid="stElementContainer"] button,
          div[data-testid="stElementContainer"]:has(.ahkam-active) + div[data-testid="stElementContainer"] button,
          div[data-testid="stElementContainer"]:has(.ahkam-active) ~ div[data-testid="stElementContainer"] button {
            background: linear-gradient(180deg, #15803d, #166534) !important;
            color: #ffffff !important;
            border-color: #14532d !important;
          }
          div[data-testid="stElementContainer"]:has(.makhraj-active) + div[data-testid="stElementContainer"] button:hover,
          div[data-testid="stElementContainer"]:has(.makhraj-active) ~ div[data-testid="stElementContainer"] button:hover,
          div[data-testid="stElementContainer"]:has(.ahkam-active) + div[data-testid="stElementContainer"] button:hover,
          div[data-testid="stElementContainer"]:has(.ahkam-active) ~ div[data-testid="stElementContainer"] button:hover {
            background: linear-gradient(180deg, #166534, #14532d) !important;
          }

          /* Mobile responsive layout overrides to prevent vertical column stacking and scrolling */
          @media (max-width: 991px) {
            .block-container {
              padding: 0.4rem 0.15rem 52px 0.15rem !important;
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

            /* 1. Prevent ANY horizontal block from collapsing into a vertical column on mobile */
            div[data-testid="stHorizontalBlock"] {
              display: flex !important;
              flex-direction: row !important;
              flex-wrap: nowrap !important;
              width: 100% !important;
              gap: 4px !important;
              align-items: center !important;
            }
            div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
            [data-testid="stColumn"],
            [data-testid="column"] {
              width: auto !important;
              min-width: 0 !important;
              flex: 1 1 0% !important;
              padding: 0 !important;
            }

            /* Login screen on mobile */
            .login-card-container {
              width: 100% !important;
              max-width: 380px !important;
              margin: 1.5vh auto !important;
              padding: 0 6px !important;
              box-sizing: border-box !important;
            }
            .login-card-container div[data-testid="stLayoutWrapper"] {
              width: 100% !important;
              background: #ffffff !important;
              border-radius: 14px !important;
              box-shadow: 0 4px 20px rgba(30, 26, 18, 0.08) !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.login-header-anchor) > div[data-testid="stColumn"]:nth-child(1),
            div[data-testid="stHorizontalBlock"]:has(.login-header-anchor) > div[data-testid="column"]:nth-child(1) {
              flex: 1 1 calc(100% - 60px) !important;
              min-width: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.login-header-anchor) > div[data-testid="stColumn"]:nth-child(2),
            div[data-testid="stHorizontalBlock"]:has(.login-header-anchor) > div[data-testid="column"]:nth-child(2) {
              flex: 0 0 54px !important;
              width: 54px !important;
              min-width: 54px !important;
            }

            /* 2. Top Header Bar (AMSB Title + Fullscreen + Logout) */
            div[data-testid="stHorizontalBlock"]:has(.header-row-anchor) {
              margin-bottom: 2px !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.header-row-anchor) > div[data-testid="stColumn"]:nth-child(1),
            div[data-testid="stHorizontalBlock"]:has(.header-row-anchor) > div[data-testid="column"]:nth-child(1) {
              flex: 1 1 auto !important;
              min-width: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.header-row-anchor) > div[data-testid="stColumn"]:nth-child(2),
            div[data-testid="stHorizontalBlock"]:has(.header-row-anchor) > div[data-testid="column"]:nth-child(2) {
              flex: 0 0 52px !important;
              width: 52px !important;
              min-width: 52px !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.header-row-anchor) > div[data-testid="stColumn"]:nth-child(3),
            div[data-testid="stHorizontalBlock"]:has(.header-row-anchor) > div[data-testid="column"]:nth-child(3) {
              flex: 0 0 48px !important;
              width: 48px !important;
              min-width: 48px !important;
            }

            /* 3. Top Student Bar (Luxury Pill + Switch Button Row) */
            div[data-testid="stHorizontalBlock"]:has(.student-luxury-pill) {
              margin-bottom: 3px !important;
              align-items: center !important;
              gap: 5px !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.student-luxury-pill) > div[data-testid="stColumn"]:nth-child(1),
            div[data-testid="stHorizontalBlock"]:has(.student-luxury-pill) > div[data-testid="column"]:nth-child(1) {
              flex: 1 1 calc(100% - 76px) !important;
              min-width: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.student-luxury-pill) > div[data-testid="stColumn"]:nth-child(2),
            div[data-testid="stHorizontalBlock"]:has(.student-luxury-pill) > div[data-testid="column"]:nth-child(2) {
              flex: 0 0 72px !important;
              width: 72px !important;
              min-width: 72px !important;
            }
            .student-luxury-pill {
              display: flex !important;
              align-items: center !important;
              gap: 6px !important;
              background: linear-gradient(135deg, #ffffff 0%, #faf6ec 100%) !important;
              border: 1px solid rgba(184, 137, 23, 0.45) !important;
              border-left: 3.5px solid var(--emerald) !important;
              border-radius: 8px !important;
              padding: 2px 8px !important;
              height: 27px !important;
              min-height: 27px !important;
              box-shadow: 0 1px 4px rgba(14, 107, 80, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
              overflow: hidden !important;
              white-space: nowrap !important;
              cursor: pointer !important;
              box-sizing: border-box !important;
            }
            .student-avatar-badge {
              font-size: 12px !important;
              background: rgba(14, 107, 80, 0.12) !important;
              color: var(--emerald) !important;
              border-radius: 50% !important;
              width: 18px !important;
              height: 18px !important;
              display: flex !important;
              align-items: center !important;
              justify-content: center !important;
              flex-shrink: 0 !important;
              line-height: 1 !important;
            }
            .student-title-text {
              font-size: 11.5px !important;
              font-weight: 700 !important;
              color: #064e3b !important;
              letter-spacing: -0.15px !important;
              overflow: hidden !important;
              text-overflow: ellipsis !important;
              white-space: nowrap !important;
              font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            }
            .student-change-btn-wrapper,
            .student-change-btn-wrapper .stButton {
              width: 100% !important;
            }
            .student-change-btn-wrapper .stButton > button,
            div[data-testid="stHorizontalBlock"]:has(.student-luxury-pill) .stButton > button {
              height: 27px !important;
              min-height: 27px !important;
              font-size: 10.5px !important;
              font-weight: 700 !important;
              background: linear-gradient(180deg, #ffffff, #fef9ee) !important;
              color: #854d0e !important;
              border: 1px solid rgba(184, 137, 23, 0.5) !important;
              border-radius: 8px !important;
              padding: 0 4px !important;
              line-height: 1.1 !important;
              box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
              white-space: nowrap !important;
            }

            /* Bottom Thumb-Zone Dock Container (Fixed at bottom on all devices) */
            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) {
              position: fixed !important;
              bottom: 0px !important;
              left: 50% !important;
              transform: translateX(-50%) !important;
              width: 100% !important;
              max-width: 480px !important;
              z-index: 999999 !important;
              background: rgba(255, 255, 255, 0.98) !important;
              backdrop-filter: blur(16px) !important;
              -webkit-backdrop-filter: blur(16px) !important;
              border-top: 2px solid var(--emerald) !important;
              border-left: none !important;
              border-right: none !important;
              border-bottom: none !important;
              box-shadow: 0 -3px 16px rgba(0, 0, 0, 0.10) !important;
              padding: 2px 4px 3px 4px !important;
              margin: 0 !important;
              border-radius: 12px 12px 0 0 !important;
            }

            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) div[data-testid="stVerticalBlock"] {
              gap: 2px !important;
            }

            /* Ensure horizontal rows inside bottom dock stay in a single row */
            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) div[data-testid="stHorizontalBlock"] {
              display: flex !important;
              flex-direction: row !important;
              flex-wrap: nowrap !important;
              width: 100% !important;
              gap: 3px !important;
              margin: 0 !important;
              align-items: center !important;
            }

            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
              flex: 1 1 0% !important;
              min-width: 0 !important;
              padding: 0 !important;
            }

            /* Dock tab buttons */
            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) .stButton > button {
              height: 31px !important;
              min-height: 31px !important;
              font-size: 10.5px !important;
              font-weight: 700 !important;
              padding: 1px 2px !important;
              line-height: 1.1 !important;
              border-radius: 8px !important;
              white-space: nowrap !important;
              overflow: hidden !important;
              text-overflow: ellipsis !important;
              letter-spacing: -0.2px !important;
              box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
            }

            /* Active primary button in dock */
            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) .stButton > button[kind="primary"],
            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) .stButton > button[data-testid="stBaseButton-primary"] {
              background: linear-gradient(180deg, var(--emerald), #084c39) !important;
              color: #ffffff !important;
              border: 1px solid var(--gold) !important;
              box-shadow: 0 2px 8px rgba(14, 107, 80, 0.35) !important;
            }

            /* Inactive secondary button in dock */
            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) .stButton > button[kind="secondary"],
            div[data-testid="stLayoutWrapper"]:has(.mobile-bottom-dock-anchor) .stButton > button[data-testid="stBaseButton-secondary"] {
              background: #f1f5f9 !important;
              color: #334155 !important;
              border: 1px solid #cbd5e1 !important;
            }

            /* Sub-tray for utility pages */
            div[data-testid="stHorizontalBlock"]:has(.dock-tray-anchor) {
              margin-bottom: 3px !important;
              padding-bottom: 4px !important;
              border-bottom: 1px dashed rgba(14, 107, 80, 0.2) !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.dock-tray-anchor) .stButton > button {
              height: 26px !important;
              min-height: 26px !important;
              font-size: 9.5px !important;
            }

            /* 4. Homework & Title Row */
            div[data-testid="stHorizontalBlock"]:has(.hw-row-anchor) {
              margin-bottom: 2px !important;
              min-height: 20px !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.hw-row-anchor) > div[data-testid="stColumn"]:nth-child(1),
            div[data-testid="stHorizontalBlock"]:has(.hw-row-anchor) > div[data-testid="column"]:nth-child(1) {
              flex: 0 0 auto !important;
              min-width: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.hw-row-anchor) > div[data-testid="stColumn"]:nth-child(2),
            div[data-testid="stHorizontalBlock"]:has(.hw-row-anchor) > div[data-testid="column"]:nth-child(2) {
              flex: 1 1 auto !important;
              min-width: 0 !important;
            }

            /* 5. Sipara selector + Subtract toggle inline on mobile */
            div[data-testid="stHorizontalBlock"]:has(.sipara-row-anchor) {
              margin-bottom: 3px !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.sipara-row-anchor) > div[data-testid="stColumn"]:nth-child(1),
            div[data-testid="stHorizontalBlock"]:has(.sipara-row-anchor) > div[data-testid="column"]:nth-child(1) {
              flex: 1 1 calc(100% - 70px) !important;
              min-width: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.sipara-row-anchor) > div[data-testid="stColumn"]:nth-child(2),
            div[data-testid="stHorizontalBlock"]:has(.sipara-row-anchor) > div[data-testid="column"]:nth-child(2) {
              flex: 0 0 66px !important;
              width: 66px !important;
              min-width: 66px !important;
            }

            /* Jadeed Surah selector row on mobile */
            .jadeed-surah-row {
              width: 100% !important;
              margin-bottom: 3px !important;
            }
            .jadeed-surah-row [data-baseweb="select"] {
              width: 100% !important;
            }

            /* 6. Card Containers (Hifz, Ahkam, Makharij) */
            div[data-testid="stVerticalBlockBorderWrapper"],
            div[data-testid="stLayoutWrapper"]:not(:has(.mobile-bottom-dock-anchor)) {
              margin-bottom: 3px !important;
              border-radius: 8px !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] > div,
            div[data-testid="stLayoutWrapper"]:not(:has(.mobile-bottom-dock-anchor)) > div {
              padding: 3px 6px !important;
              gap: 2px !important;
            }
            .hifz-card-anchor,
            .ahkam-card-anchor,
            .makharij-card-anchor {
              display: block !important;
              height: auto !important;
              line-height: 1.1 !important;
              margin: 0 0 1px 0 !important;
              padding: 0 !important;
            }
            div:has(> .hifz-card-anchor),
            div:has(> .ahkam-card-anchor),
            div:has(> .makharij-card-anchor),
            div[data-testid="stElementContainer"]:has(.hifz-card-anchor),
            div[data-testid="stElementContainer"]:has(.ahkam-card-anchor),
            div[data-testid="stElementContainer"]:has(.makharij-card-anchor),
            div[data-testid="stElementContainer"]:has(.hw-row-anchor),
            div[data-testid="stElementContainer"]:has(.hifz-card-anchor) *,
            div[data-testid="stElementContainer"]:has(.ahkam-card-anchor) *,
            div[data-testid="stElementContainer"]:has(.makharij-card-anchor) * {
              min-height: 15px !important;
              height: auto !important;
              font-size: 11px !important;
            }

            /* 7. Symmetrical 3-column mistake rows (I'rab) on mobile */
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="stColumn"]:nth-child(3), div[data-testid="column"]:nth-child(3)) > div:nth-child(1),
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="stColumn"]:nth-child(3), div[data-testid="column"]:nth-child(3)) > div:nth-child(3) {
              flex: 0 0 26px !important;
              width: 26px !important;
              max-width: 26px !important;
              min-width: 26px !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="stColumn"]:nth-child(3), div[data-testid="column"]:nth-child(3)) > div:nth-child(2) {
              flex: 1 1 0% !important;
              min-width: 0 !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"]:has(div[data-testid="stColumn"]:nth-child(3), div[data-testid="column"]:nth-child(3)) .stButton > button {
              width: 26px !important;
              max-width: 26px !important;
              height: 22px !important;
              min-height: 22px !important;
              padding: 0 !important;
              font-size: 11px !important;
            }

            /* 8. Make ALL buttons very compact and prevent overflowing */
            .stButton, div[data-testid="stFormSubmitButton"] {
              border: none !important;
              background: transparent !important;
              box-shadow: none !important;
              padding: 0 !important;
              margin: 0 !important;
            }
            .stButton > button, div[data-testid="stFormSubmitButton"] > button {
              width: 100% !important;
              padding: 1px 2px !important;
              font-size: 9.5px !important;
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

            /* 9. Makharij Arabic font sizing overrides for mobile */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.makharij-card-anchor) .stButton > button,
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.makharij-card-anchor) .stButton > button *,
            div[data-testid="stLayoutWrapper"]:has(.makharij-card-anchor) .stButton > button,
            div[data-testid="stLayoutWrapper"]:has(.makharij-card-anchor) .stButton > button * {
              font-family: 'Amiri', 'Noto Naskh Arabic', 'Simplified Arabic', serif !important;
              font-size: 13.5px !important;
              font-weight: 700 !important;
              overflow: visible !important;
              line-height: 1 !important;
              height: 23px !important;
              min-height: 23px !important;
              padding: 0 !important;
              margin: 0 !important;
            }

            /* 10. Main container compact padding on mobile (60px bottom padding ensures zero dock overlap) */
            [data-testid="stMainBlockContainer"],
            .block-container {
              padding: 4px 6px 60px 6px !important;
            }
            div[data-testid="stVerticalBlock"] {
              gap: 2px !important;
            }

            /* Adjust titles and texts */
            h3 {
              font-size: 0.9rem !important;
              margin: 0 !important;
            }
            div[data-testid="stVerticalBlock"] p,
            div[data-testid="stVerticalBlock"] span,
            div[data-testid="stVerticalBlock"] div {
              font-size: 10px !important;
            }
            hr {
              margin: 0.2rem 0 !important;
            }
          }

          /* Float selectbox popover dropdowns to top of screen on short/landscape mobile view to avoid keyboard overlaps */
          @media (max-height: 480px) {
            div[data-baseweb="popover"] {
              z-index: 999999 !important;
              box-shadow: 0 10px 30px rgba(30,26,18,0.25) !important;
            }
            /* Reset Popper.js dynamic translate3d/top offsets on all intermediate wrappers */
            div[data-baseweb="popover"] div:not([data-baseweb="menu"]) {
              transform: none !important;
              top: 0 !important;
              left: 0 !important;
              right: 0 !important;
              position: relative !important;
            }
            div[data-baseweb="menu"] {
              max-height: 100px !important;
              overflow-y: auto !important;
              border: 2px solid var(--gold) !important;
              border-radius: 10px !important;
              background-color: rgba(255, 255, 255, 0.98) !important;
              padding: 4px 0 !important;
            }
            div[data-baseweb="menu"] ul {
              margin: 0 !important;
              padding: 0 !important;
              max-height: 100px !important;
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
        <script>
          (function() {
            function updateScrollTop() {
              const y = window.scrollY || window.pageYOffset || 0;
              document.documentElement.style.setProperty('--scroll-top', y + 'px');
            }
            window.addEventListener('scroll', updateScrollTop, { passive: true });
            window.addEventListener('resize', updateScrollTop, { passive: true });
            document.addEventListener('focusin', function() {
              setTimeout(updateScrollTop, 100);
              setTimeout(updateScrollTop, 300);
              setTimeout(updateScrollTop, 500);
            });
            updateScrollTop();

            // Real-time popover aligner to place selectbox dropdown directly ABOVE the active input on short viewports
            function alignPopover() {
              try {
                // Only activate on short screens (e.g. mobile landscape or keyboard open)
                if (window.innerHeight > 480) return;

                const popover = document.querySelector('div[data-baseweb="popover"]');
                if (!popover) return;
                
                // Reset Popper.js dynamic translate3d/top offsets on all intermediate wrappers
                const wrappers = popover.querySelectorAll('div');
                wrappers.forEach(div => {
                  if (div.getAttribute('data-baseweb') !== 'menu') {
                    div.style.setProperty('transform', 'none', 'important');
                    div.style.setProperty('top', '0', 'important');
                    div.style.setProperty('left', '0', 'important');
                    div.style.setProperty('position', 'relative', 'important');
                  }
                });
                
                const activeInput = document.activeElement;
                if (!activeInput || activeInput.tagName !== 'INPUT') return;
                
                // Check if it is a Streamlit selectbox combobox input
                const isCombobox = activeInput.getAttribute('role') === 'combobox' || 
                                   activeInput.getAttribute('aria-autocomplete') === 'list' ||
                                   activeInput.id.includes('select');
                if (!isCombobox) return;
                
                const inputRect = activeInput.getBoundingClientRect();
                const scrollTop = window.scrollY || document.documentElement.scrollTop;
                const scrollLeft = window.scrollX || document.documentElement.scrollLeft;
                
                const popoverHeight = popover.offsetHeight || 100;
                
                // Position popover directly ABOVE the input field
                popover.style.setProperty('position', 'absolute', 'important');
                popover.style.setProperty('top', (inputRect.top + scrollTop - popoverHeight - 4) + 'px', 'important');
                popover.style.setProperty('left', (inputRect.left + scrollLeft) + 'px', 'important');
                popover.style.setProperty('width', inputRect.width + 'px', 'important');
                popover.style.setProperty('transform', 'none', 'important');
                popover.style.setProperty('bottom', 'auto', 'important');
              } catch (e) {}
            }
            
            // Run aligner frequently (50ms interval) for real-time tracking
            setInterval(alignPopover, 50);
          })();
        </script>
        """,
        unsafe_allow_html=True,
    )

