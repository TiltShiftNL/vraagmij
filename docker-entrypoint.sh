#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

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