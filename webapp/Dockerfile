FROM ubuntu:20.04 

RUN apt-get update 
RUN apt-get install -y python3.9
RUN apt-get install -y python3-pip
RUN apt-get install -y curl \
    libboost-dev \
    libboost-date-time-dev \
    libboost-thread-dev \
    zlib1g-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    libopenexr-dev \
    autoconf
 
RUN mkdir /tmp/pids

RUN curl -k -O -L https://github.com/POV-Ray/povray/archive/refs/tags/v3.7.0.10.tar.gz && \
    tar xzvf v3.7.0.10.tar.gz && \
    cd povray-3.7.0.10/unix && \
    ./prebuild.sh && \
    cd ../ && \
    ./configure  COMPILED_BY="Blajak Szlejiznic <szlej@iznic.com>" && \
    make && \
    make install

WORKDIR /opt

EXPOSE 5000

RUN pip install pipenv

# We copy just the Pipfile first to leverage Docker cache
COPY ./Pipfile* /opt/


ENV PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

RUN pipenv lock && \
    pipenv requirements > requirements.txt && \
    pip install -r requirements.txt

