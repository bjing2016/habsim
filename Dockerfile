FROM ubuntu:18.04

# Install system dependencies
RUN apt-get update
RUN apt-get install -qq -y git curl wget nano pkg-config libfreetype6-dev libpng-dev zlib1g-dev gfortran apt-utils cron

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install python 3
RUN apt-get install -qq -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -qq -y python3.7 python3-pip python3-dev
ENV DEBIAN_FRONTEND=noninteractive

RUN pip3 install Flask

ADD crontab /etc/cron.d/main-cron
RUN chmod 0644 /etc/cron.d/main-cron
RUN crontab /etc/cron.d/main-cron
RUN touch /var/log/cron.log

RUN mkdir -p /home/run
WORKDIR /home/run
EXPOSE 5000

ENV FLASK_APP=api.py
CMD service cron start && flask run --host=0.0.0.0