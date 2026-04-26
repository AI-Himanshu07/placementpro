#!/usr/bin/env bash

python manage.py migrate
python manage.py shell < create_superuser.py