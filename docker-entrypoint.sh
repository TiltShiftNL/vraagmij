#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

echo "Test nginx"
nginx -t

echo "Start nginx"
/etc/init.d/nginx start

echo "Start supervisord"
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

echo "DONE"

# systemctl reload nginx

# tail -F -n0 /etc/hosts
# tail -f /var/log/nginx/access.log