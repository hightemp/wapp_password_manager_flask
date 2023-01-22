#!/bin/bash

# CFILE=wapp_password_manager_flask
# timestamp=$(date +%s)
# VERSION=$(echo `cat VERSION`.$timestamp)

# git add .
# git commit -am "`date` update"
# git tag $VERSION
# git push

# if [ "$?" != "0" ]; then
#     echo "====================================================="
#     echo "ERROR"
#     echo
#     exit 1
# fi

# echo "[!] " gh release create $VERSION -t $VERSION -n '""' --target main
# gh release create $VERSION -t $VERSION -n "" --target main

# # cd ..
# # python3 -m zipapp $CFILE -p "/usr/bin/env python3"
# # echo $PWD/$CFILE.pyz
# # cd $CFILE

# pyinstaller -F --path "." --add-data "templates:templates" --add-data "static:static" --hidden-import "main" --hidden-import "baselib" --hidden-import "database" --hidden-import "request_vars" __main__.py
# cp dist/__main__ ../"{$CFILE}.bin"

# gh release upload $VERSION ../"{$CFILE}.bin" --clobber

CFILE=wapp_password_manager_flask
timestamp=$(date +%s)
VERSION=$(echo `cat VERSION`.$timestamp)

git add .
git commit -am "`date` update"
git tag $VERSION
git push

if [ "$?" != "0" ]; then
    echo "====================================================="
    echo "ERROR"
    echo
    exit 1
fi

echo "[!] " gh release create $VERSION -t $VERSION -n '""' --target main
gh release create $VERSION -t $VERSION -n "" --target main

if [ "$1" == "pyinst" -o "$1" == "all" ]; then
    ./build.sh pyinst
    cp dist/__main__ ../"${CFILE}.bin"
    gh release upload $VERSION ../"${CFILE}.bin" --clobber
fi
if [ "$1" == "pyinst_docker" -o "$1" == "all" ]; then
    ./build.sh pyinst_docker
    cp dist/__main__ ../"${CFILE}__all.bin"
    gh release upload $VERSION ../"${CFILE}.bin" --clobber
fi
if [ "$1" == "zipapp" -o "$1" == "all" ]; then
    ./build.sh zipapp
    gh release upload $VERSION ../"${CFILE}.pyz" --clobber
fi
