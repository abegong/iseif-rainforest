# ISEIF Rainforest Logger

## What does it do?
For a defined set of users, fetch instantaneous Rainforest data at regular six-second intervals and store it to disk. Every hour, rotate those logs to permanent storage on S3.


## Deployment
We use [docker](https://www.docker.com/), so this should only take a few minutes. There are three steps.

### 1. Build each of the images.
(You only have to do this once when you launch a new EC2 instance or change the source code.)

        docker build -t iseif-base docker/base/
        docker build -t iseif-code app
        docker build -t iseif-server docker/server/
        docker build -t iseif-pinger docker/pinger/

This structure uses docker's stacking capability to save time when rebuilding images. The iseif-base image installs all the dependencies for the app---this one takes a few minutes to build. The iseif-code image installs the code from iseif_rainforest/app/. This is quick.

### 2. Run `docker-compose up`
This command will launch containers for the three services defined in the docker-compse.yml config: redis, server, and pinger.

You can confirm that the containers are running with the command `docker ps`. The output should have rows for three containers, like this:

    CONTAINER ID        IMAGE                 COMMAND                  CREATED             STATUS              PORTS                     NAMES
    e1d6af5e464a        iseif-pinger:latest   "python pinger.py --a"   8 hours ago         Up 8 hours                                    iseifrainforest_pinger_1
    077dad0b012b        iseif-server:latest   "python app.py --redi"   8 hours ago         Up 8 hours          0.0.0.0:32768->8000/tcp   iseifrainforest_server_1
    b03f68fec7c2        redis                 "/entrypoint.sh redis"   9 hours ago         Up 9 hours          6379/tcp                  iseifrainforest_redis_1

### For troubleshooting:

`docker-compose up pinger` will start up the pinger container in a verbose mode. This is a good first line of defense if the service fails to start up.

`docker exec -i -t iseifrainforest_server_1 bash` will give you bash console access to the server container. Great for logging in to poke around.

### 3. Add user records to redis

!!! TBD.

## Architecture

### 1. Redis
Serves as a local cache for user login information, and a little bit of metadata. Each key-value pair corresponds to a user.

Keys are user cloud_ids stored as strings, including leading zeroes.
  
Values are stringified json blobs with the following fields.

    {
        'cloud_id' : "002738",
        'user_email' : 'viktor.krum@durmstrang.edu',
        'user_pw' : '1234567',
        'total_events_logged' : 2725,
        'first_timestamp' : 1443274732.39435,
        'last_timestamp' : 1443277732.933939,
    }

### 2. Server
The server exposes these routes:

	GET /api/event/{user_cloud_id} : fetch instantaneous Rainforest data for a given user
	POST /api/user/{user_cloud_id} : create or update a user records cached in redis

### 3. Pinger

!!!

## Codebase

## Milestones

What's done?
* The inner loop of the code runs reliably
* The main methods for EagleDataLogger are under test
* General architecture is stable and (mostly) documented
* Deployment is dockerized

What's not done?
* Logs are not yet stored to S3.
* Add monitoring and error logging for deployment
* Refactor the code for scalability : make HTTP calls non-blocking, maintain a persistent pool of file connections in app.py
* Develop utility scripts for starting (sharded) container sets
* Security on the server is (literally) a joke. Fix that, maybe.
* Do we need to capture pricing data?
* Make certain that the system handles edge case (bad credentials, unavailable Eagles, etc.) gracefully.

