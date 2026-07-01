"""Subprocess helpers for CLI integration tests."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
CLI_TIMEOUT = 5.0


def cli_env() -> dict[str, str]:
    env = os.environ.copy()
    current = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_DIR) if not current else os.pathsep.join([str(SRC_DIR), current])
    return env


def module_command(*args: str) -> list[str]:
    return [sys.executable, "-m", "py_dlt_client", *args]


def run_module_cli(args: Sequence[str], *, timeout: float = CLI_TIMEOUT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        module_command(*args),
        cwd=REPO_ROOT,
        env=cli_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
