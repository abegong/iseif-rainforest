# ISEIF Rainforest Logger

## What does it do?
For a defined set of users, fetch instantaneous Rainforest data at regular six-second intervals. Store results to logs on disk. Every hour, rotate those logs to permanent storage on S3.


## Deployment
We use [docker](https://www.docker.com/), so this should only take a few minutes. There are three steps.

### 1. Build each of the images.
(You only have to do this once when you launch a new EC2 instance or change the source code.)

        docker build -t iseif-base docker/base/
        docker build -t iseif-code app

This structure uses docker's stacking capability to save time when rebuilding images. The iseif-base image installs all the dependencies for the app---this one takes a few minutes to build. The iseif-code image installs the code from iseif_rainforest/app/. This is quick.

### 2. Run `docker-compose up`
This command will launch containers for the three services defined in the docker-compse.yml config: redis, server, and pinger.

Note: You MUST have your AWS credentials defined as ENV variables (AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID) when you run this command. Otherwise, fetching data and logging to disk will work, but logging to S3 will fail.

You can confirm that the containers are running with the command `docker ps`. The output should have rows for three containers, like this:

    CONTAINER ID        IMAGE                 COMMAND                  CREATED             STATUS              PORTS                     NAMES
    e1d6af5e464a        iseif-pinger:latest   "python pinger.py --a"   8 hours ago         Up 8 hours                                    iseifrainforest_pinger_1
    077dad0b012b        iseif-server:latest   "python app.py --redi"   8 hours ago         Up 8 hours          0.0.0.0:32768->8000/tcp   iseifrainforest_server_1
    b03f68fec7c2        redis                 "/entrypoint.sh redis"   9 hours ago         Up 9 hours          6379/tcp                  iseifrainforest_redis_1

### For troubleshooting:

`docker-compose up pinger` will start up the pinger container in a verbose mode. This is a good first line of defense if the service fails to start up.

`docker exec -i -t iseifrainforest_server_1 bash` will give you bash console access to the server container. Great for logging in to poke around.

### 3. Add user records

    python scripts/add_user_info_via_server.py

This command requires a file containing user_info entries on separate rows. Each line must be an individual json blob containing all the expected fields (see the Redis section below.)

After you run this command, the pinger service should pick up on the new records and begin requesting data within a minute.


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
    POST /api/users/{user_cloud_id}?pw={password} : create or update a user records cached in redis
    GET  /api/users/{user_cloud_id}?pw={password} : fetch user records cached in redis
    GET  /api/users/?pw={password} : fetch a list of user records cached in redis
    
The users/ routes have the flimsiest of security: the pw parameter must be set to 'plaintext123'. The event/ API has no password protection, but it will fail if the requested `cloud_id` isn't a valid key in redis.

### 3. Pinger

This service is an infinite loop that requests user data every six seconds. In addition, it refreshes its list of users from redis once a minute.

## Codebase

*Service libraries*

    app.py                : The primary tornado server.
    pinger.py             : A CLI tool for running the pinger service.
    rotate_logs_to_s3.py  : A single-method CLI tool to rotate logs to S3
    
*Utility libraries*

    logger.py             : Shared functions, wrapped in a single state-free function.
    util.py               : Simple utility functions
    eagle_http.py         : A set of utility functions for the Eagle REST API. Based loosely on the buggy and unpythonic methods in this repo: https://github.com/rainforestautomation/Eagle-Http-API

*Misc*

    tests.py              : unit tests. Run with `$ nosetests` from the app/ directory.
    run_logger.py         : A CLI for logger.py; somewhat out of date. (We used this for testing before app.py was developed; haven't needed it much since then.)

## Logs

Service logs are stored here:
    
    /data/logs/server/server.log
    /data/logs/pinger/pinger.log
    /data/logs/rotate/rotate.log

By default, these logs are set up for INFO-level logging. You can configure these settings using command-line arguments. In production, you can configure them from docker-compose.yml.

User data logs are stored in filepaths like this:

    /data/logs/2015-09-27-04/iseif-rainforest-002506-2015-09-27-04.jl 
    /data/logs/[Y-M-D-H]/iseif-rainforest-[user_cloud_id]-[Y-M-D-H].jl 

User data logs in S3 are stored to the `agong-iseif-temp` bucket. (Not the right place for long-term storage.) The filepaths (i.e. key names) look like this:

    rainforest-logs/002506/2015/09/28/iseif-rainforest-002506-2015-09-28-16.jl
    rainforest-logs/[user_cloud_id]/YYYY/MM/DD/iseif-rainforest-[user_cloud_id]-[Y-M-D-H].jl

The filepath format for the server is different from S3 because the "query" pattern for each is different. On the server, logs are stored temporarily with the intent to rotate every hour. Therefore, the filepath emphasizes time, putting logs for every user in a common directory.

On S3, the primary data retrieval mode will most likely be by user. Therefore, files are stored with user_cloud_id leading the filepath.

Ignoring the filepath, the filename itself is always the same. It documents cloud_id and time, so that the source of the data is always clear.

## Milestones

What's done?
* The inner loop of the code runs reliably
* The main methods for EagleDataLogger are under test
* General architecture is stable and (mostly) documented
* Deployment is dockerized
* Add monitoring and error logging for deployment
* Logs are rotated to S3 every hour.

What's not done?
* Refactor the code for scalability : make HTTP calls non-blocking, maintain a persistent pool of file connections in app.py
* Develop utility scripts for starting (sharded) container sets
* Security on the server is (literally) a joke. Fix that, maybe.
* Do we need to capture pricing data?
* Make certain that the system handles edge case (bad credentials, unavailable Eagles, etc.) gracefully.

