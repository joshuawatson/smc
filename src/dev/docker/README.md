# SageMathCloud Docker image

This is a self-contained single-image multi-user SageMathCloud server.

**STATUS:**
  - Actually should be reasonably secure -- the database has a long random password, user accounts are separate, etc.
  - No quotas are implemented except idle timeout.
  - Sagetex not setup yet.

## Instructions

To store your local SMC data in the directory ~/smc, and run SageMathCloud (via docker), make sure you have about 7GB disk space free, then type:

     docker run -v ~/smc:/projects -P williamstein/sagemathcloud

Type `docker ps` to see what port were exposed, and connect to either the encrypted or non-encrypted ports.

    docker ps

which might output

    CONTAINER ID        IMAGE                        COMMAND                 CREATED             STATUS              PORTS                                           NAMES
    9eff7133bbd6        williamstein/sagemathcloud   "/bin/sh -c ./run.py"   3 minutes ago       Up 3 minutes        0.0.0.0:32779->80/tcp, 0.0.0.0:32778->443/tcp   evil_almeida

If the port is 32779 (as it is above), then visit http://localhost:32779/

If you're running this docker image on a remote server and want to use
ssh port forwarding to connect, type

    ssh -L 8080:localhost:32779 username@remote_server

then open your web browser to http://localhost:8080

### Make all users admins

    $ docker exec -it 9eff7133bbd6 bash
    root@9eff7133bbd6:/# cd /smc/src
    root@9eff7133bbd6:/smc/src# . smc-env
    root@9eff7133bbd6:/smc/src# coffee
    coffee> require 'c'; db()
    coffee> db.table('accounts').update(groups:['admin']).run(done())

Refresh your browser, and then you should see an "Admin edit..." button in any project's settings.

## Issues

  - gp doesn't work at all, due to the Ubuntu ppa being broken


## Build

Build the image

    make build

Run the image (to test)

    make run

How I pushed this

    docker tag smc:latest williamstein/sagemathcloud
    docker login --username=williamstein
    docker push  williamstein/sagemathcloud
