# balfolk-db
The tools to import and export the dances for bal folk music

# Usage
## Windows
After installing you will find a shortcut in your start menu.

## Linux
You might need to install the correct python version (3.8) if you want to run the binary. 

## Logging
Every run appends to `music_wizard.log` in the user's home directory. Ask for that file
when someone reports a problem: it holds the full traceback of a failed synchronization
and a warning whenever a server endpoint answers with something unexpected.

# Dependencies
- Python3
  - Mutagen
  - pydub
  - appJar
  - requests

## Not available via pip install
  - Tkinter
  
## cx-Freeze
### Dependencies
#### System
 - python3-dev

#### Python environment   
 - cx-freeze

## Windows
```
python setup.py build
python setup.py bdist_msi
```

### Building Windows from Linux
cx_Freeze does not cross-compile, so the Windows build runs on GitHub instead:
Actions -> "Windows build" -> Run workflow (or push a `v*` tag). The MSI lands in the
run's artifacts. The workflow downloads `ffmpeg.exe`/`ffprobe.exe`/`fpcalc.exe` and
applies the pydub patches itself, so nothing Windows-specific is needed locally.


I.e.
```
cxfreeze tools\music_wizard.py --include-path="C:\Users\Wim Lemkens\Documents\Projects\balfolk-db\tools" --include-modules=tools,Music
cxfreeze music_wizard.py --include-path="C:\Users\Wim Lemkens\Documents\Projects\balfolk-db\tools" --include-modules=tools,Music
```

## Linux
```
source venv/bin/activate
cxfreeze tools/music_wizard.py --include-path=</path/to/code> --include-modules=tools,Music,idna.idnadata
```

I.e: 
```
cxfreeze balfolk-db/tools/music_wizard.py --include-path=balfolk-db/ --include-modules=tools,Music,idna.idnadata && mkdir -p dist/balfolk-db && cp -r balfolk-db/images dist/balfolk-db/images
```

### AppImage
```
source venv/bin/activate
python setup.py bdist_appimage
```
Result: `dist/music_wizard-<version>-x86_64.AppImage`, where the version comes from
`tools/version.py` (bump it before building, or you overwrite the previous one).

Requirements:
 - `lib/ffmpeg` and `lib/ffprobe`: static Linux builds (e.g. from
   https://johnvansickle.com/ffmpeg/), marked executable. `setup.py` bundles them next
   to the frozen binary so pydub works without a system ffmpeg.
 - FUSE (`libfuse2`) to *run* the resulting AppImage. Not needed to build it, and
   `./music_wizard-*.AppImage --appimage-extract-and-run` works without it.

cx_Freeze downloads `appimagetool` to `~/.local/bin/` on first build. If you already
have it somewhere else: `python setup.py bdist_appimage --appimagetool=/path/to/appimagetool`.
