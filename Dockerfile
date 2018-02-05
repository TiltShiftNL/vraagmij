FROM python:3.6

ENV DEBIAN_FRONTEND=noninteractive
ENV DOCKER_CONTAINER=1
ENV DJANGO_ENV=notset
ENV POSTGRES_DB=notset
ENV POSTGRES_HOST=notset
ENV POSTGRES_USER=notset
ENV POSTGRES_PASSWORD=notset
ENV STATIC_ROOT '/opt/static_root/'

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y
RUN apt-get install -y nginx
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y --no-install-recommends supervisor && \
    pip3 install uwsgi

COPY jeugdzorg /opt/app
RUN mkdir /opt/static_root/
RUN mkdir /var/uwsgi/
RUN usermod -a -G root www-data
RUN newgrp www-data
RUN newgrp root
COPY jeugdzorg/django_nginx.conf /etc/nginx/sites-enabled
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
RUN chmod 777 /etc/nginx/sites-enabled/django_nginx.conf

WORKDIR /opt/app

RUN pip3 install -r ./requirements.txt

EXPOSE 80

CMD "/usr/local/bin/docker-entrypoint.sh"