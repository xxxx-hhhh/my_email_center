#!/usr/bin/env bash

if [ ! -d './migrations' ]; then
    python ./manage.py db init
fi

python ./manage.py db migrate
python ./manage.py db upgrade
