FROM python:3-bookworm

RUN apt update && apt upgrade -y
RUN apt install -y python3-full python-is-python3 python3-pip

ADD . /backend

WORKDIR /backend
RUN pip install --break-system-packages -r requirements.txt

ENV DJANGO_SUPERUSER_USERNAME="root"
ENV DJANGO_SUPERUSER_PASSWORD="root"
ENV DJANGO_SUPERUSER_EMAIL="root@root.tld"

RUN echo cd /backend > /run.sh
RUN echo python manage.py migrate >> /run.sh
RUN echo python manage.py createsuperuser --no-input >> /run.sh
RUN echo python manage.py runserver 0.0.0.0:8000 >> /run.sh

WORKDIR /

# django port
EXPOSE 8000
CMD ["bash", "run.sh"]
