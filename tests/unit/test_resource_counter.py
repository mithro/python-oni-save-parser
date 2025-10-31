"""Tests for resource_counter example script."""

import subprocess
import sys
from pathlib import Path

import pytest


def test_resource_counter_help():
    """Should display help message."""
    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Count resources" in result.stdout or "resource" in result.stdout.lower()
