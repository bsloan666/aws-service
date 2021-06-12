AWS-service
===========

An example web server that adds two numbers
-------------------------------------------
Simple UWSGI web server in a docker container. To test locally in Docker Desktop:

```
# 1. clone repo  
git clone git@github.com:bsloan666/aws-service.git

# 2. change directory to source root
cd aws-service/

# 3. create a /pids/ directory at the root of your host
sudo mkdir /pids

# 4. In Docker Preferences->Resources->File Sharing
# share the newly created /pids/ directory

# 5. build container
docker-compose build

# 6. run container
docker-compose up -d

# 7. point browser at: 
http://127.0.0.1:5000/sum/add2
```

Installing on an AWS EC2 instance
---------------------------------
It is nearly a repeat of the steps for running on one's  local workstation, with two exceptions. 

 - 1) The minimally configured Amazon Linux instance does not have git, docker or docker-compose, so they must be installed
 - 2) Permissions for the EC2 default user are probably not configured as on your local workstation, so either 
      - a) some directories will have to have their access permissions changed or
      - b) most install/build/run commands will need to be run with the sudo prefix


On the AWS management console webpage, 

 - 1) configure the security group associated with your instance to accept incoming Custom TCP communications on port 5000. Then...
 - 2) download the access key pair file for your user
```
# 1. log in to the AWS EC2 instance
ssh -i /path-to-key-pair-file/key-pair-file.pem ec2-user@<DNS-name-of-instance-server>.<region>.compute.amazonaws.com

# 2. Install build dependencies 

sudo yum install -y git 
sudo yum install -y docker 
sudo yum install -y docker-compose

# 3. Follow steps 1-3 above (same as testing locally) 

# 4. Follow steps 5 and 6 above 

# 5. point browser at <DNS-name-of-instance-server>.<region>.compute.amazonaws.com:5000/sum/add2
```
