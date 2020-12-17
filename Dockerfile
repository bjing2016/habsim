# Note: we are no longer using Docker

FROM ubuntu:18.04

# Install system dependencies
RUN apt-get update
RUN apt-get install -qq -y git curl wget nano pkg-config libfreetype6-dev libpng-dev zlib1g-dev gfortran apt-utils cron htop lsof

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install python 3
RUN apt-get install -qq -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -qq -y python3.7 python3-pip python3-dev
ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get install -qq -y libproj-dev proj-bin proj-data libtcmalloc-minimal4 libhdf5-serial-dev python3-grib
RUN pip3 install numpy

RUN pip3 install Flask
RUN pip3 install flask-cors

# ADD crontab /etc/cron.d/main-cron
# RUN chmod 0644 /etc/cron.d/main-cron
# RUN crontab /etc/cron.d/main-cron
# RUN touch /var/log/cron.log

RUN mkdir -p /home/run
RUN mkdir -p /gefs/gefs
WORKDIR /home/run
EXPOSE 5000

# ADD elevinit.sh elevinit.sh
# RUN bash elevinit.sh

CMD flask run --host=0.0.0.0
# Run with --port=80 as suitable.
