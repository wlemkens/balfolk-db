import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
        "includes": ["tools","Music","tkinter"],
        "include_files": [
                          ("images/login.png", "images/login.png"),
                          ("images/dances_local.png", "images/dances_local.png"),
                          ("images/dances_remote.png", "images/dances_remote.png"),
                          ("images/language.png", "images/language.png"),
                          ("images/library.png", "images/library.png"),
                          ("images/local_to_remote.png", "images/local_to_remote.png"),
                          ("images/prepsync.png", "images/prepsync.png"),
                          ("images/remote_to_local.png", "images/remote_to_local.png"),
                          ("images/sync.png", "images/sync.png")
                          ]
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
   base = "Win32GUI"
    build_exe_options["include_files"] += ["tools/ffmpeg.exe",
                          "tools/ffprobe.exe",
                          "tools/ffplay.exe"]


setup(  name = "music_wizard",
        description = "BalfolkDB Music Wizard",
        options = {"build_exe": build_exe_options},
        executables = [Executable("tools/music_wizard.py", base=base)])

