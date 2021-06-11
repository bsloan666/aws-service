AWS-service
===========

An example web server that adds two numbers
-------------------------------------------

Simple UWSGI web server in a docker container. To test locally in Docker Desktop:

```
# clone repo  
git clone git@github.com:bsloan666/aws-service.git

# change directory to source root
cd aws-service/

# create a /pids/ directory at the root of your host
sudo mkdir /pids

# In Docker Preferences->Resources->File Sharing
# share the newly created /pids/ directory

# build container
docker-compose build

# run container
docker-compose up -d

# point browser at: 
http://127.0.0.1:5000/sum/add2
```
