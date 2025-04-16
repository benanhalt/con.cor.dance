

serve:
    poetry run pelican -r -l

build:
    poetry run pelican content -s publishconf.py

publish: build
    rsync -rva output con.cor.dance:
