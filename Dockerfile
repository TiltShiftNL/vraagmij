FROM python:3.6

RUN apt-get update && \
    apt-get install -y && \
    pip3 install uwsgi

COPY jeugdzorg /opt/app

RUN pip3 install -r /opt/app/requirements.txt

ENV DJANGO_ENV=prod
ENV DOCKER_CONTAINER=1

EXPOSE 8000

#CMD ["uwsgi", "--ini", "/opt/app/uwsgi.ini", "--py-autoreload", "1"]
#CMD ["python", "/opt/app/manage.py", "runserver"]