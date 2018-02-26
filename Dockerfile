FROM python:3.6

ENV DEBIAN_FRONTEND=noninteractive
ENV DOCKER_CONTAINER=1
ENV DJANGO_ENV=notset
ENV POSTGRES_DB=notset
ENV POSTGRES_HOST=notset
ENV POSTGRES_USER=notset
ENV POSTGRES_PASSWORD=notset
ENV STATIC_ROOT '/opt/static_root/'
ENV PYTHONHASHSEED 0
ENV ENV=production

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y
RUN apt-get install -y nginx
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y --no-install-recommends apache2-utils
RUN apt-get install -y --no-install-recommends cron
RUN apt-get install -y --no-install-recommends supervisor && \
    pip3 install uwsgi

RUN mkdir /opt/static_root/
RUN mkdir /opt/file_upload/
RUN mkdir /opt/git/
RUN mkdir /var/uwsgi/

COPY .git /opt/git
COPY jeugdzorg /opt/app
COPY jeugdzorg/nginx_production.conf /opt/
COPY jeugdzorg/nginx_acceptance.conf /opt/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY jeugdzorg/crontab /etc/cron.d/crontab
COPY jeugdzorg/update_regelingen.sh /usr/local/bin/update_regelingen.sh

RUN usermod -a -G root www-data
RUN newgrp www-data
RUN newgrp root

RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
RUN chmod 777 /usr/local/bin/update_regelingen.sh
RUN chmod 0644 /etc/cron.d/crontab
RUN touch /var/log/cron.log
#RUN chmod 777 /etc/nginx/sites-enabled/nginx_production.conf
#RUN chmod 777 /etc/nginx/sites-enabled/nginx_acceptance.conf

WORKDIR /opt/app

RUN pip3 install -r ./requirements.txt

EXPOSE 80

CMD "/usr/local/bin/docker-entrypoint.sh"