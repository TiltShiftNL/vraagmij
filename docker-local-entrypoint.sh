#!/bin/bash

GIT_REV="$( cd /opt/git/ ; git rev-parse HEAD)"

rm -rf /opt/git/

echo $GIT_REV > /opt/git_rev

echo "Add cron jobs"
/etc/init.d/cron start
python manage.py crontab add

echo "Apply database migrations"
python manage.py migrate

python manage.py createsuperuser_pw  --username ${ADMIN_USERNAME} --password ${ADMIN_PASSWORD} --noinput --email 'admin@host.com'

export OS_USERNAME="fixxx7_acc"
export OS_PASSWORD="..."
export OS_AUTH_URL="https://identity.stack.cloudvps.com/v2.0"
export OS_TENANT_ID="2d195c35ab9e4bafac2d76efb556964e"
export OS_TENANT_NAME="BGE000081 fixxx7_acc"
export OS_REGION_NAME="NL"

if [ "${RUNSERVER}" == "no" ];
then
    echo "Don't start server"
    tail -f /etc/hosts
else
    echo "Start server"
    python ./manage.py runserver 0.0.0.0:8000 --settings jeugdzorg.settings.develop
fi
