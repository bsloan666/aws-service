FROM ubuntu:20.04 

RUN apt-get update 
RUN apt-get install -y python3.8
RUN apt-get install -y python3-pip

WORKDIR /opt

EXPOSE 5000

RUN pip install pipenv

# We copy just the Pipfile first to leverage Docker cache
COPY ./Pipfile* /opt/


ENV PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

RUN pipenv lock --requirements > requirements.txt && \
    pip install -r requirements.txt

