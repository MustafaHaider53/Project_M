from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_key: str


def get_settings() -> Settings:
    url = (st.secrets.get("SUPABASE_URL") or "").strip()
    key = (st.secrets.get("SUPABASE_KEY") or "").strip()
    return Settings(supabase_url=url, supabase_key=key)

