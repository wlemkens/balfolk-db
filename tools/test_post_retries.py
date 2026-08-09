"""Self-check for post_with_retries. Run: venv/bin/python -m tools.test_post_retries"""
import tools.common as common
from tools.common import post_with_retries
import requests


def _run():
    common.time.sleep = lambda s: None  # don't actually wait during the test

    # succeeds on the 3rd attempt -> returns, no raise
    calls = {"n": 0}
    def flaky(*a, **k):
        calls["n"] += 1
        if calls["n"] < 3:
            raise requests.exceptions.ConnectionError("boom")
        return "OK"
    common.requests.post = flaky
    assert post_with_retries("url", retries=5) == "OK"
    assert calls["n"] == 3, calls["n"]

    # always fails -> tries retries+1 times then re-raises the last exception
    calls["n"] = 0
    def dead(*a, **k):
        calls["n"] += 1
        raise requests.exceptions.Timeout("nope")
    common.requests.post = dead
    try:
        post_with_retries("url", retries=5)
        assert False, "should have raised"
    except requests.exceptions.Timeout:
        pass
    assert calls["n"] == 6, calls["n"]  # 1 initial + 5 retries

    # non-transient error is NOT retried
    calls["n"] = 0
    def http_err(*a, **k):
        calls["n"] += 1
        raise requests.exceptions.HTTPError("400")
    common.requests.post = http_err
    try:
        post_with_retries("url", retries=5)
        assert False, "should have raised"
    except requests.exceptions.HTTPError:
        pass
    assert calls["n"] == 1, calls["n"]

    print("post_with_retries: all checks passed")


if __name__ == "__main__":
    _run()
