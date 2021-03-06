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
ENV TZ=Europe/Amsterdam

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get dist-upgrade -y
RUN apt-get install -y nginx
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y --no-install-recommends apache2-utils
RUN apt-get install -y --no-install-recommends cron
RUN apt-get install -y --no-install-recommends vim
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
COPY jeugdzorg/check_user_activity.sh /usr/local/bin/check_user_activity.sh
COPY jeugdzorg/send_update_mail.sh /usr/local/bin/send_update_mail.sh
COPY jeugdzorg/gebruiker_email_verificatie.sh /usr/local/bin/gebruiker_email_verificatie.sh
COPY jeugdzorg/create_crontabs.sh /usr/local/bin/create_crontabs.sh
COPY jeugdzorg/mail_account_active_check.sh /usr/local/bin/mail_account_active_check.sh
COPY jeugdzorg/set_cronjob_worker.sh /usr/local/bin/set_cronjob_worker.sh
# COPY project_env.sh /root/project_env.sh

RUN usermod -a -G root www-data
RUN newgrp www-data
RUN newgrp root

# RUN chmod 777 /root/project_env.sh
RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
RUN chmod 777 /usr/local/bin/update_regelingen.sh
RUN chmod 777 /usr/local/bin/check_user_activity.sh
RUN chmod 777 /usr/local/bin/send_update_mail.sh
RUN chmod 777 /usr/local/bin/gebruiker_email_verificatie.sh
RUN chmod 777 /usr/local/bin/create_crontabs.sh
RUN chmod 777 /usr/local/bin/mail_account_active_check.sh
RUN chmod 777 /usr/local/bin/set_cronjob_worker.sh
RUN chmod 0644 /etc/cron.d/crontab
RUN touch /var/log/cron.log
#RUN chmod 777 /etc/nginx/sites-enabled/nginx_production.conf
#RUN chmod 777 /etc/nginx/sites-enabled/nginx_acceptance.conf

WORKDIR /opt/app

RUN pip install --upgrade pip
RUN pip3 install -r ./requirements.txt

EXPOSE 80

CMD "/usr/local/bin/docker-entrypoint.sh"