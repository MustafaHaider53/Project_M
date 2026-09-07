from __future__ import annotations

import time
from typing import Dict, Any, Tuple
import streamlit as st


def _get_timer_key(module_name: str, student_id: str) -> str:
    return f"recitation_timer_{module_name.lower()}_{student_id}"


def get_timer_state(module_name: str, student_id: str, target_minutes: int) -> Dict[str, Any]:
    key = _get_timer_key(module_name, student_id)
    if key not in st.session_state:
        st.session_state[key] = {
            "elapsed_seconds": 0,
            "is_running": False,
            "last_start_ts": None,
            "target_seconds": target_minutes * 60,
        }
    state = st.session_state[key]
    state["target_seconds"] = target_minutes * 60
    return state


def update_timer_elapsed(state: Dict[str, Any]) -> int:
    """Calculates true elapsed wall-clock seconds if running."""
    if state.get("is_running") and state.get("last_start_ts") is not None:
        now = time.time()
        delta = int(now - state["last_start_ts"])
        return state.get("elapsed_seconds", 0) + max(0, delta)
    return state.get("elapsed_seconds", 0)


def start_timer(module_name: str, student_id: str, target_minutes: int) -> None:
    state = get_timer_state(module_name, student_id, target_minutes)
    if not state.get("is_running"):
        state["is_running"] = True
        state["last_start_ts"] = time.time()


def _sync_db_session_duration(module_name: str, student_id: str, elapsed_seconds: int, target_minutes: int) -> None:
    try:
        mod = module_name.lower()
        sid = st.session_state.get(f"{mod}_session_id")
        if sid:
            from app.db import update_session_duration
            is_over = elapsed_seconds > (target_minutes * 60)
            update_session_duration(sid, elapsed_seconds, is_over)
    except Exception:
        pass


def pause_timer(module_name: str, student_id: str, target_minutes: int) -> None:
    state = get_timer_state(module_name, student_id, target_minutes)
    if state.get("is_running"):
        final_elapsed = update_timer_elapsed(state)
        state["elapsed_seconds"] = final_elapsed
        state["is_running"] = False
        state["last_start_ts"] = None
        _sync_db_session_duration(module_name, student_id, final_elapsed, target_minutes)


def reset_timer(module_name: str, student_id: str, target_minutes: int) -> None:
    state = get_timer_state(module_name, student_id, target_minutes)
    state["elapsed_seconds"] = 0
    state["is_running"] = False
    state["last_start_ts"] = None
    _sync_db_session_duration(module_name, student_id, 0, target_minutes)


def stop_and_capture_timer(module_name: str, student_id: str, target_minutes: int) -> int:
    state = get_timer_state(module_name, student_id, target_minutes)
    final_seconds = update_timer_elapsed(state)
    state["elapsed_seconds"] = final_seconds
    state["is_running"] = False
    state["last_start_ts"] = None
    _sync_db_session_duration(module_name, student_id, final_seconds, target_minutes)
    return final_seconds


def sync_active_module_timers(current_module: str, student_id: str) -> None:
    """
    Auto-pauses other module timers when switching tabs,
    ensuring a student's timer freezes when leaving and resumes on return.
    """
    if not student_id:
        return
    all_modules = [("murajat", 10), ("juzulhali", 15), ("jadeed", 5)]
    for mod, target_m in all_modules:
        if mod != current_module.lower():
            key = _get_timer_key(mod, student_id)
            if key in st.session_state and st.session_state[key].get("is_running"):
                final_elapsed = update_timer_elapsed(st.session_state[key])
                st.session_state[key]["elapsed_seconds"] = final_elapsed
                st.session_state[key]["is_running"] = False
                st.session_state[key]["last_start_ts"] = None
                _sync_db_session_duration(mod, student_id, final_elapsed, target_m)


def render_recitation_timer(
    *,
    module_name: str,
    target_minutes: int,
    student_id: str,
    auto_start: bool = False,
    compact: bool = False
) -> Tuple[int, bool, bool]:
    """
    Renders an interactive recitation timer card with:
    - Real-time client-side live ticking (JS)
    - Pause / Resume / Reset controls
    - Overtime visual alerts (Turn 🔴 Red when elapsed > target_minutes)
    - Returns (elapsed_seconds, is_running, is_overtime)
    """
    if not student_id:
        return 0, False, False

    # Synchronize module active state
    sync_active_module_timers(module_name, student_id)

    state = get_timer_state(module_name, student_id, target_minutes)
    
    # Auto-start if requested and not yet started
    if auto_start and not state.get("is_running") and state.get("elapsed_seconds", 0) == 0:
        state["is_running"] = True
        state["last_start_ts"] = time.time()

    current_elapsed = update_timer_elapsed(state)
    target_secs = target_minutes * 60
    is_running = state.get("is_running", False)
    is_overtime = current_elapsed > target_secs

    # Format minutes:seconds
    mins = current_elapsed // 60
    secs = current_elapsed % 60
    time_str = f"{mins:02d}:{secs:02d}"
    target_str = f"{target_minutes:02d}:00"

    overtime_mins = (current_elapsed - target_secs) // 60 if is_overtime else 0
    overtime_secs = (current_elapsed - target_secs) % 60 if is_overtime else 0
    overtime_str = f"+{overtime_mins:02d}:{overtime_secs:02d} Overtime"

    # Component styling
    border_color = "#ef4444" if is_overtime else ("#10b981" if is_running else "#cbd5e1")
    bg_color = "#fef2f2" if is_overtime else ("#f0fdf4" if is_running else "#f8fafc")
    text_color = "#b91c1c" if is_overtime else ("#047857" if is_running else "#334155")
    status_label = "🔴 OVERTIME" if is_overtime else ("🟢 RECITER ACTIVE" if is_running else "⏸️ PAUSED")
    
    is_running_js = "true" if is_running else "false"
    
    timer_component_html = f"""
    <div id="timer_card_{module_name}" style="
        background: {bg_color};
        border: 1.5px solid {border_color};
        border-radius: 8px;
        padding: 5px 12px;
        display: flex;
        align-items: center;
        height: 48px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        box-sizing: border-box;
        margin-bottom: 2px;
    ">
        <span style="font-size: 17px; margin-right: 8px;">⏱️</span>
        <div>
            <div id="timer_status_{module_name}" style="
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: {text_color};
                line-height: 1.1;
            ">{status_label} • Target: {target_str}</div>
            <div id="timer_digits_container_{module_name}" style="
                font-size: 17px;
                font-weight: 800;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                color: {text_color};
                line-height: 1.2;
                display: flex;
                align-items: center;
            ">
                <span id="display_digits_{module_name}">{time_str}</span>
                <span id="overtime_digits_{module_name}" style="
                    font-size: 11px;
                    font-weight: bold;
                    color: #b91c1c;
                    margin-left: 6px;
                    display: {'inline' if is_overtime else 'none'};
                ">{f"({overtime_str})" if is_overtime else ""}</span>
            </div>
        </div>
    </div>
    <script>
    (function() {{
        window.__timer_intervals = window.__timer_intervals || {{}};
        if (window.__timer_intervals["{module_name}"]) {{
            clearInterval(window.__timer_intervals["{module_name}"]);
        }}
        
        const cardEl = document.getElementById("timer_card_{module_name}");
        const elDigits = document.getElementById("display_digits_{module_name}");
        const elOver = document.getElementById("overtime_digits_{module_name}");
        const elStatus = document.getElementById("timer_status_{module_name}");
        const elContainer = document.getElementById("timer_digits_container_{module_name}");
        const isRunning = {is_running_js};
        const targetSecs = {target_secs};
        const targetStr = "{target_str}";
        let elapsed = {current_elapsed};
        
        function updateDisplay(sec) {{
            const m = Math.floor(sec / 60);
            const s = sec % 60;
            const mStr = String(m).padStart(2, '0');
            const sStr = String(s).padStart(2, '0');
            if (elDigits) {{
                elDigits.textContent = mStr + ":" + sStr;
            }}
            
            if (sec > targetSecs) {{
                const overSec = sec - targetSecs;
                const overM = Math.floor(overSec / 60);
                const overS = overSec % 60;
                if (elOver) {{
                    elOver.textContent = "(+" + String(overM).padStart(2, '0') + ":" + String(overS).padStart(2, '0') + " Overtime)";
                    elOver.style.display = "inline";
                }}
                if (cardEl) {{
                    cardEl.style.backgroundColor = "#fef2f2";
                    cardEl.style.borderColor = "#ef4444";
                }}
                if (elStatus) {{
                    elStatus.textContent = "🔴 OVERTIME • Target: " + targetStr;
                    elStatus.style.color = "#b91c1c";
                }}
                if (elContainer) {{
                    elContainer.style.color = "#b91c1c";
                }}
            }} else {{
                if (elOver) {{
                    elOver.textContent = "";
                    elOver.style.display = "none";
                }}
                if (cardEl) {{
                    cardEl.style.backgroundColor = isRunning ? "#f0fdf4" : "#f8fafc";
                    cardEl.style.borderColor = isRunning ? "#10b981" : "#cbd5e1";
                }}
                if (elStatus) {{
                    elStatus.textContent = (isRunning ? "🟢 RECITER ACTIVE" : "⏸️ PAUSED") + " • Target: " + targetStr;
                    elStatus.style.color = isRunning ? "#047857" : "#334155";
                }}
                if (elContainer) {{
                    elContainer.style.color = isRunning ? "#047857" : "#334155";
                }}
            }}
        }}

        updateDisplay(elapsed);

        if (isRunning) {{
            window.__timer_intervals["{module_name}"] = setInterval(function() {{
                elapsed++;
                updateDisplay(elapsed);
            }}, 1000);
        }}
    }})();
    </script>
    """

    col_widget, col_ctrls = st.columns([2.5, 1.5])
    with col_widget:
        st.html(timer_component_html, unsafe_allow_javascript=True)
    with col_ctrls:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if is_running:
                if st.button("⏸️ Pause", key=f"btn_pause_{module_name}", width="stretch"):
                    pause_timer(module_name, student_id, target_minutes)
                    st.rerun()
            else:
                if st.button("▶ Start" if current_elapsed == 0 else "▶ Resume", type="primary", key=f"btn_start_{module_name}", width="stretch"):
                    start_timer(module_name, student_id, target_minutes)
                    st.rerun()
        with c_btn2:
            if st.button("🔄 Reset", key=f"btn_reset_{module_name}", width="stretch", disabled=(current_elapsed == 0 and not is_running)):
                reset_timer(module_name, student_id, target_minutes)
                st.rerun()

    return current_elapsed, is_running, is_overtime
