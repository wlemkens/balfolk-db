# balfolk-db
The tools to import and export the dances for bal folk music

# Dependencies
- Python3
  - Mutagen
  - mysql-connector -> should be removed
  - pydub
  - appJar
  - requests

## Not available via pip install
  - Tkinter
  
# cx-Freeze
## Windows
```
python setup.py build
python setup.py bdist_msi
```

I.e.
```
cxfreeze tools\music_wizard.py --include-path="C:\Users\Wim Lemkens\Documents\Projects\balfolk-db\tools" --include-modules=tools,Music
cxfreeze music_wizard.py --include-path="C:\Users\Wim Lemkens\Documents\Projects\balfolk-db\tools" --include-modules=tools,Music```

## Linux
source venv/bin/activate
cxfreeze tools/music_wizard.py --include-path=</path/to/code> --include-modules=tools,Music,idna.idnadata
