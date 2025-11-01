# Verification Workflow

## Commitment

**Before claiming any work is complete, I will run `python verify.py` and show the results.**

This ensures:
- No regressions in type checking (mypy --strict)
- No linting errors (ruff check)
- No formatting violations (ruff format)
- All unit tests pass (pytest tests/unit/)
- All benchmark tests are collectible

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

## What This Means

### ❌ NEVER say without verification:
- "Tests pass"
- "All checks pass"
- "No errors"
- "Should work now"
- "Looks correct"
- "Fixed"
- "Done"
- "Complete"

### ✅ ALWAYS do:
1. Make changes
2. Run `python verify.py`
3. Read full output
4. Check exit code
5. ONLY THEN make claims with evidence

## Examples

### ❌ Wrong (no evidence):
```
"I've fixed the type errors. All tests should pass now."
```

### ✅ Correct (with evidence):
```
"I've fixed the type errors. Running verification:

[Runs python verify.py]

Result: All 5 checks passed:
- mypy --strict: Success (54 files)
- ruff check: All checks passed
- ruff format: 55 files formatted
- pytest unit: 240 tests passed
- pytest benchmark: 14 tests collected

Exit code: 0

All checks pass. Safe to commit."
```

## When to Verify

Run `python verify.py` before:

1. **Committing any code**
2. **Creating pull requests**
3. **Claiming work is complete**
4. **Moving to the next task**
5. **Saying anything that implies success**

## Quick Check

For faster iteration during development:
```bash
python verify.py --quick  # Skips benchmark collection
```

Full check before commit:
```bash
python verify.py  # Run all checks
```

## Verification Script Output

The script will show:
- ✅ PASS - Check succeeded
- ❌ FAIL - Check failed (with details)

Exit codes:
- 0 = All checks passed, safe to proceed
- 1 = Some checks failed, DO NOT commit

## Why This Matters

From the verification-before-completion skill:
- Claims without evidence = dishonesty, not efficiency
- "Should pass" ≠ actually passes
- Partial verification proves nothing
- Exhaustion is not an excuse
- Trust must be earned with evidence

## Current Baseline

As of 2025-11-01:
- 54 Python source files
- 240 unit tests
- 14 benchmark tests
- 0 mypy errors (strict mode)
- 0 ruff errors
- 0 test failures

This baseline must not regress.
