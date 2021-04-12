# balfolk-db
The tools to import and export the dances for bal folk music

# Dependencies
- Python3
  - Mutagen
  - pydub
  - appJar
  - requests

## Not available via pip install
  - Tkinter
  
# Windows pydub changes
Use the supplied patches to patch pydub in order to prevent dos popups.

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
