#!/bin/bash

GIT_REV="$( cd /opt/git/ ; git rev-parse HEAD)"

rm -rf /opt/git/

echo $GIT_REV > /opt/git_rev

echo "Add cron jobs"
/etc/init.d/cron start
# python manage.py crontab add

echo "START Create initial migrations"
python manage.py clear_db_migrations
python manage.py migrate --fake
# python manage.py migrate --fake-initial
echo "END Create initial migrations"

echo "Apply database migrations"

python manage.py migrate

python manage.py createcachetable

python manage.py set_cronjob_worker

python manage.py createsuperuser_pw  --username ${ADMIN_USERNAME} --password ${ADMIN_PASSWORD} --noinput --email 'admin@host.com'

if [ "${RUNSERVER}" == "no" ];
then
    echo "Don't start server"
    tail -f /etc/hosts
else
    echo "Start server"
    python ./manage.py runserver 0.0.0.0:8000 --settings jeugdzorg.settings.develop
fi
