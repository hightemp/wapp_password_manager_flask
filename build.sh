#!/bin/bash

# cd ..
# rm -f ./$CFILE.database.db
# pyinstaller $CFILE/__main__.spec
# $CFILE/dist/__main__  --bind 0.0.0.0:5010

# rm -f ./$CFILE.database.db
# pyinstaller __main__.spec
# dist/__main__  --bind 0.0.0.0:5010

# pyinstaller -F --path "." --add-data "templates:templates" --add-data "static:static" --hidden-import "main" --hidden-import "baselib" --hidden-import "database" --hidden-import "request_vars" __main__.py
# cp dist/__main__ ../$CFILE
# cd ..
# $CFILE  --bind 0.0.0.0:5010

# python3 -m zipapp $CFILE -p "/usr/bin/env python3"
# echo $PWD/$CFILE.pyz

#./$CFILE.pyz --bind 0.0.0.0:5010

#!/bin/bash

CFILE=wapp_password_manager_flask
PORT=5010

PYINSTALLER=pyinstaller
PYINSTALLER_DOCKER="docker run -v $PWD:/src fydeinc/pyinstaller "
PYINSTALLER_DOCKER="docker run -v $PWD:/src/ cdrx/pyinstaller-linux:python3"
PYINSTALLER_BUILD="docker build -t $CFILE/pyinstaller-linux:python3 . "
PYINSTALLER_DOCKER="docker run -v $PWD:/src/ $CFILE/pyinstaller-linux:python3 "
PYINSTALLER_DOCKER_PARAMS=" -F --path . --add-data=templates:templates --add-data=static:static --hidden-import 'main' --hidden-import 'baselib' --hidden-import 'database' --hidden-import 'request_vars' __main__.py"

echo '__DEBUG__='>.env
if [ "$1" == "flask" ]; then
    echo '__DEBUG__=1' > .env
    export FLASK_DEBUG=1
    export FLASK_APP=main.py 
    python3 -m flask run --extra-files . --with-threads -h0.0.0.0 -p$PORT
elif [ "$1" == "flask_db_init" ]; then
    echo '__DEBUG__=1' > .env
    export FLASK_DEBUG=1
    export FLASK_APP=__init__.py 
    python3 -m flask db init
elif [ "$1" == "flask_db_migrate" ]; then
    echo '__DEBUG__=1' > .env
    export FLASK_DEBUG=1
    export FLASK_APP=__init__.py 
    python3 -m flask db migrate
elif [ "$1" == "pyinst" ]; then
    $PYINSTALLER $PYINSTALLER_DOCKER_PARAMS
    cp dist/__main__ ../$CFILE.bin
    if [ "$2" == "run" ]; then
        ../$CFILE.bin  --bind 0.0.0.0:$PORT -w 10
    fi
elif [ "$1" == "pyinst_docker" ]; then
    docker build -t $CFILE/pyinstaller-linux:python3 .
    $PYINSTALLER_DOCKER "$PYINSTALLER $PYINSTALLER_DOCKER_PARAMS"
    cp dist/__main__ ../$CFILE.bin
    if [ "$2" == "run" ]; then
        ../$CFILE.bin  --bind 0.0.0.0:$PORT -w 10
    fi
elif [ "$1" == "zipapp" ]; then
    # cp .env ..
    cd ..
    python3 -m zipapp $CFILE -p "/usr/bin/env python3"
    rm ./$CFILE.database.db
    echo $PWD/$CFILE.pyz
    if [ "$2" == "run" ]; then
        ./$CFILE.pyz --bind 0.0.0.0:$PORT -w 10
    fi
fi

