FROM python:3.6

ENV DEBIAN_FRONTEND=noninteractive
ENV DOCKER_CONTAINER=1
ENV DJANGO_ENV=notset
ENV POSTGRES_DB=notset
ENV POSTGRES_HOST=notset
ENV POSTGRES_USER=notset
ENV POSTGRES_PASSWORD=notset

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y --no-install-recommends supervisor && \
    pip3 install uwsgi

COPY jeugdzorg /opt/app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY docker-local-entrypoint.sh /usr/local/bin/docker-local-entrypoint.sh

RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
RUN chmod 777 /usr/local/bin/docker-local-entrypoint.sh

WORKDIR /opt/app

RUN pip3 install -r ./requirements.txt

EXPOSE 80

#CMD ["uwsgi", "--ini", "/opt/app/uwsgi.ini", "--py-autoreload", "1"]

#CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
CMD "/usr/local/bin/docker-entrypoint.sh"