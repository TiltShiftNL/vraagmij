#!/bin/bash

GIT_REV="$( cd /opt/git/ ; git rev-parse HEAD)"

rm -rf /opt/git/

echo $GIT_REV > /opt/git_rev

cp /opt/nginx_$ENV.conf /etc/nginx/sites-enabled/

chmod 777 /etc/nginx/sites-enabled/nginx_$ENV.conf
# chmod 777 /var/log/nginx/nginx_error.log
# chmod 777 /var/log/nginx/nginx_access.log

# printenv | sed 's/^\(.*\)$/export \1/g' | grep -E "^export POSTGRES" > /root/project_env.sh

cat <<EOF > /root/project_env.sh
export ENV=${ENV}
export POSTGRES_DB=${POSTGRES_DB}
export POSTGRES_HOST=${POSTGRES_HOST}
export POSTGRES_USER=${POSTGRES_USER}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
export ADMIN_USERNAME=${ADMIN_USERNAME}
export ADMIN_PASSWORD=${ADMIN_PASSWORD}
export GIT_REV=${GIT_REV}
EOF



htpasswd -cb /opt/.htpasswd jeugdzorg fixxx7

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

python manage.py create_crontabs

echo "Add cron jobs"
/etc/init.d/cron start
# python manage.py crontab add
# python manage.py crontab show

# echo "START Create initial migrations"
# python manage.py clear_db_migrations
# python manage.py migrate --fake
# python manage.py migrate --fake-initial
# echo "END Create initial migrations"

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