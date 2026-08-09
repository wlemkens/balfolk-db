"""Self-check for fpcalc output parsing. Run: venv/bin/python -m tools.test_fingerprint"""
from tools.common import _parse_fpcalc


def _run():
    fp, dur = _parse_fpcalc("DURATION=225\nFINGERPRINT=AQADtEmikYkUjZKC\n")
    assert fp == "AQADtEmikYkUjZKC", fp
    assert dur == 225.0, dur

    # order-independent, tolerant of blank/garbage lines
    fp, dur = _parse_fpcalc("\nFINGERPRINT=X\nDURATION=12.5\njunk\n")
    assert fp == "X" and dur == 12.5, (fp, dur)

    # fpcalc failed / no fingerprint -> (None, None), never a crash
    assert _parse_fpcalc("") == (None, None)
    assert _parse_fpcalc("DURATION=10") == (None, None)

    print("fingerprint parsing: all checks passed")


if __name__ == "__main__":
    _run()
