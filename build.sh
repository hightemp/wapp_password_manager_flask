#!/bin/bash

CFILE=wapp_password_manager_flask

# cd ..
# rm -f ./$CFILE.database.db
# pyinstaller $CFILE/__main__.spec
# $CFILE/dist/__main__  --bind 0.0.0.0:5010

# rm -f ./$CFILE.database.db
# pyinstaller __main__.spec
# dist/__main__  --bind 0.0.0.0:5010

pyinstaller -F --path "." --add-data "templates:templates" --add-data "static:static" --hidden-import "main" --hidden-import "baselib" --hidden-import "database" --hidden-import "request_vars" __main__.py
dist/__main__  --bind 0.0.0.0:5010

# python3 -m zipapp $CFILE -p "/usr/bin/env python3"
# echo $PWD/$CFILE.pyz

#./$CFILE.pyz --bind 0.0.0.0:5010
