#!/bin/bash

GIT_REV="$( cd /opt/git/ ; git rev-parse HEAD)"

rm -rf /opt/git/

echo $GIT_REV > /opt/git_rev

cp /opt/nginx_$ENV.conf /etc/nginx/sites-enabled/

chmod 777 /etc/nginx/sites-enabled/nginx_$ENV.conf
# chmod 777 /var/log/nginx/nginx_error.log
# chmod 777 /var/log/nginx/nginx_access.log

printenv | sed 's/^\(.*\)$/export \1/g' | grep -E "^export POSTGRES" > /root/project_env.sh

htpasswd -c /opt/.htpasswd "jeugdzorg" "fixxx7"

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

echo "Add cron jobs"
/etc/init.d/cron start
# python manage.py crontab add
# python manage.py crontab show

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

python manage.py createsuperuser_pw  --username ${ADMIN_USERNAME} --password ${ADMIN_PASSWORD} --noinput --email 'admin@host.com'

echo "Test nginx"
nginx -t

echo "Start nginx"
/etc/init.d/nginx start

echo "Start supervisord"
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf