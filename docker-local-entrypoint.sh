#!/bin/bash

echo "Apply database migrations"
python manage.py migrate

python manage.py createsuperuser_pw  --username ${ADMIN_USERNAME} --password ${ADMIN_PASSWORD} --noinput --email 'admin@host.com'

tail -f /etc/hosts
# python ./manage.py runserver 0.0.0.0:8000 --settings jeugdzorg.settings.develop