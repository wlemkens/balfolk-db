import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
        "includes": ["tools","Music","tkinter"],
        "excludes": ["sqlite3", "unittest", "test"],
        "include_files": [
                          ("images/login.png", "images/login.png"),
                          ("images/dances_local.png", "images/dances_local.png"),
                          ("images/dances_remote.png", "images/dances_remote.png"),
                          ("images/language.png", "images/language.png"),
                          ("images/library.png", "images/library.png"),
                          ("images/local_to_remote.png", "images/local_to_remote.png"),
                          ("images/prepsync.png", "images/prepsync.png"),
                          ("images/remote_to_local.png", "images/remote_to_local.png"),
                          ("images/sync.png", "images/sync.png"),
                          ("images/balfolkdb.ico", "images/balfolkdb.ico")
                          ]
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
executable = None
options = None
if sys.platform == "win32":
    base = "Win32GUI"
    build_exe_options["include_files"] += ["lib/ffmpeg.exe",
                          "lib/ffprobe.exe"]
    shortcut_table = [
        ("ProgramMenuShortcut",  # Shortcut
         "ProgramMenuFolder",  # Directory_
         "Balfolk DB Music Wizard",  # Name
         "TARGETDIR",  # Component_
         "[TARGETDIR]music_wizard.exe",  # Target
         None,  # Arguments
         "Application to synchronize your local balfolk music library with the online Balfolk Database.",  # Description
         None,  # Hotkey
         None,  # Icon
         0,  # IconIndex
         None,  # ShowCmd
         "TARGETDIR"  # WkDir
         )
    ]

    # Now create the table dictionary
    msi_data = {"Shortcut": shortcut_table}

    # Change some default MSI options and specify the use of the above defined tables
    bdist_msi_options = {'data': msi_data}

    options = {
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    }

else:
    options = {"build_exe": build_exe_options}


setup(  name = "music_wizard",
        version = "1.1.1",
        description = "BalfolkDB Music Wizard",
        options = options,
        executables = [Executable("tools/music_wizard.py",
                                  base=base,
                                  icon="images/balfolkdb.ico")
])

