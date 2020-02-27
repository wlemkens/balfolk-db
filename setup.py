import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = { "includes": ["tools","Music","tkinter"], "include_files": ["tools/ffmpeg.exe", "tools/ffprobe.exe", "tools/ffplay.exe"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
# if sys.platform == "win32":
#    base = "Win32GUI"


setup(  name = "music_wizard",
        description = "BalfolkDB Music Wizard",
        options = {"build_exe": build_exe_options},
        executables = [Executable("tools/music_wizard.py", base=base)])

