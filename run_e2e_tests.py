from __future__ import annotations

import sys

import pytest


def main() -> int:
    # -q: concise; -rA: show summary for all outcomes
    args = ["-q", "-rA", "tests/test_e2e_streamlit.py"]
    return int(pytest.main(args))


if __name__ == "__main__":
    raise SystemExit(main())

