"""Self-check for versionTuple. Run: venv/bin/python -m tools.test_version_compare"""
from tools.common import versionTuple


def _run():
    # the case plain string compare gets wrong
    assert versionTuple("1.10.0") > versionTuple("1.2.0")
    assert versionTuple("1.2.0") > versionTuple("1.1.7")
    assert not versionTuple("1.1.7") > versionTuple("1.2.0")

    # equal versions are not "new"
    assert not versionTuple("1.2.0") > versionTuple("1.2.0")

    # patch and major bumps
    assert versionTuple("1.2.1") > versionTuple("1.2.0")
    assert versionTuple("2.0.0") > versionTuple("1.99.99")

    print("versionTuple: all checks passed")


if __name__ == "__main__":
    _run()
