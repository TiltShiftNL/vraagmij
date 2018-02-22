#!/bin/bash

GIT_REV="$( cd /opt/git/ ; git rev-parse HEAD)"

rm -rf /opt/git/

echo $GIT_REV > /opt/git_rev

echo "Add cron jobs"
python manage.py crontab add

echo "Apply database migrations"
python manage.py migrate

python manage.py createsuperuser_pw  --username ${ADMIN_USERNAME} --password ${ADMIN_PASSWORD} --noinput --email 'admin@host.com'


if [ "${RUNSERVER}" == "no" ];
then
    echo "Don't start server"
    tail -f /etc/hosts
else
    echo "Start server"
    python ./manage.py runserver 0.0.0.0:8000 --settings jeugdzorg.settings.develop
fi
