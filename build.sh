#!/usr/bin/env bash
set -o errexit  # stop on error

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
