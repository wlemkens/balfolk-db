# Building

Before any build (`setup.py build`, `bdist_msi`, `bdist_appimage`, or triggering the
Windows workflow), verify that `host` in `tools/common.py` is `"https://balfolk-db.eu"`.
It is the only place the server is chosen, and a release pointing at the dev server
sends every user's library there. `setup.py` refuses to build when it is anything else.

Bump `tools/version.py` before building, or the new AppImage overwrites the previous one.
