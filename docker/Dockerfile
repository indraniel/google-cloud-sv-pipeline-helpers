FROM debian:stretch-slim
label maintainer "Indraniel Das <idas@wustl.edu>"

# Volumes
VOLUME /build

# bootstrap build dependencies
RUN apt-get update -qq \
    && apt-get -y install apt-transport-https \
    && echo "deb [trusted=yes] https://gitlab.com/indraniel/hall-lab-debian-repo-1/raw/master stretch main" | tee -a /etc/apt/sources.list \
    && apt-get update -qq \
    && apt-get -y install \
       build-essential \
       libcurl4-openssl-dev \
       ca-certificates \
       curl \
       --no-install-recommends

WORKDIR /build
COPY ./build-script.sh /build

RUN ["/bin/bash", "build-script.sh"]
