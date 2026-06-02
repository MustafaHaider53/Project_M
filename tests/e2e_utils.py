from __future__ import annotations

import os
import socket
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Optional


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) == 0


def wait_for_port(host: str, port: int, timeout_s: float = 30.0) -> None:
    start = time.time()
    while time.time() - start < timeout_s:
        if _is_port_open(host, port):
            return
        time.sleep(0.2)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@dataclass(frozen=True)
class StreamlitServer:
    port: int
    process: subprocess.Popen


@contextmanager
def run_streamlit_app(*, port: Optional[int] = None) -> Iterator[StreamlitServer]:
    """
    Starts Streamlit in a subprocess and yields once the port is open.
    Assumes you already have `.streamlit/secrets.toml` configured.
    """
    port = port or find_free_port()
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_SERVER_SHOW_EMAIL_PROMPT"] = "false"
    env["STREAMLIT_SERVER_PORT"] = str(port)
    env["STREAMLIT_SERVER_ADDRESS"] = "127.0.0.1"

    # Use python -m streamlit to avoid PATH issues on Windows.
    proc = subprocess.Popen(
        ["python", "-m", "streamlit", "run", "streamlit_app.py", "--server.headless=true", "--server.showEmailPrompt=false", f"--server.port={port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    try:
        wait_for_port("127.0.0.1", port, timeout_s=40)
        yield StreamlitServer(port=port, process=proc)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

