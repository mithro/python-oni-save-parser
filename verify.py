#!/usr/bin/env python3
"""Verification script to ensure no regressions before claiming completion.

This script runs all quality checks and tests to verify the codebase is in
a known-good state. Run this before:
- Committing code
- Creating pull requests
- Claiming work is complete
- Moving to the next task

Usage:
    python verify.py           # Run all checks
    python verify.py --quick   # Skip slow tests
"""

import argparse
import re
import subprocess
import sys


def run_check(
    name: str, command: list[str], success_pattern: str, timeout: int = 60
) -> tuple[bool, str]:
    """Run a verification check and return (passed, detail)."""
    print(f"Running: {name}...", flush=True)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        passed = success_pattern in result.stdout and result.returncode == 0

        # Extract details
        if "mypy" in name:
            detail = result.stdout.strip()
        elif "ruff check" in name:
            detail = result.stdout.strip()
        elif "ruff format" in name:
            detail = result.stdout.strip()
        elif "pytest" in name:
            match = re.search(r"(\d+) passed", result.stdout)
            if match:
                detail = f"{match.group(1)} tests passed"
            else:
                detail = "No tests found" if passed else result.stdout[-200:]
        else:
            detail = result.stdout.strip()[:100]

        return (passed, detail)
    except subprocess.TimeoutExpired:
        return (False, f"Timeout after {timeout}s")
    except Exception as e:
        return (False, f"Error: {str(e)}")


def main() -> int:
    """Run all verification checks."""
    parser = argparse.ArgumentParser(description="Verify codebase quality")
    parser.add_argument("--quick", action="store_true", help="Skip slow tests")
    args = parser.parse_args()

    print("=" * 70)
    print("VERIFICATION SUITE")
    print("=" * 70)
    print()

    checks = []

    # Type checking
    checks.append(
        (
            "mypy --strict",
            ["uv", "run", "mypy", ".", "--strict"],
            "Success",
            60,
        )
    )

    # Linting
    checks.append(
        (
            "ruff check",
            ["uv", "run", "ruff", "check", "."],
            "All checks passed",
            30,
        )
    )

    # Formatting
    checks.append(
        (
            "ruff format",
            ["uv", "run", "ruff", "format", "--check", "."],
            "already formatted",
            30,
        )
    )

    # Unit tests
    checks.append(
        (
            "pytest unit tests",
            ["uv", "run", "pytest", "tests/unit/", "-v", "--tb=short"],
            "passed",
            120,
        )
    )

    if not args.quick:
        # Benchmark test collection
        checks.append(
            (
                "pytest benchmark",
                ["uv", "run", "pytest", "tests/benchmark/", "--collect-only", "-q"],
                "test",
                30,
            )
        )

    results = []
    for i, (name, command, pattern, timeout) in enumerate(checks, 1):
        print(f"[{i}/{len(checks)}] {name}")
        passed, detail = run_check(name, command, pattern, timeout)
        results.append((name, passed, detail))
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"      {status}")
        if not passed:
            print(f"      {detail}")
        print()

    # Summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    all_passed = True
    for name, passed, detail in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            print(f"         {detail}")
            all_passed = False

    print()
    print("=" * 70)
    if all_passed:
        print("✅ ALL CHECKS PASSED")
        print("=" * 70)
        print()
        print("Safe to commit/complete task.")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 70)
        print()
        print("DO NOT commit or claim completion until all checks pass.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
