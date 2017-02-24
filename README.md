# PyCloud

A python wrapper daemon that manages sessions and provides a json control over the sessions with redis messaging channels.

## Installation and Updating

To install or update PyCloud it as simple of running pip3.
Run the following command as root to get started.

> $ pip3 install git+https://github.com/Year4000/PyCloud.git@v1.0.3

## Daemon Script

When installing there is a daemon script that is a wrapper for the commands bellow.

## Running

In single session mode
> python3 -m pycloud.app

In system daemon mode
> python3 -m pycloud.app --daemon

## Docker

We support Docker and when you run this in a Docker container the script string bellow will let you select other Docker images to run.
The first line is the image you want to run and the rest of the file is a json config object for `docker-py`.
The limitation is that you must give the PyCloud container access to the docker socket `/var/run/docker.sock`.
Also note that the arg `port` in the json part is the port of your application.
PyCloud will create an ephemeral port and assign it with the port on your container.

> docker run -v /var/run/docker.sock:/var/run/docker.sock year4000/pycloud

Example Script String:

```
year4000/pycloud
{
    "port": 80
}
```

## Redis Channels

- **year4000.pycloud.rank** Used for internal tracking of servers
- **year4000.pycloud.create** Used to create a node, the payload is a JSON string
- **year4000.pycloud.status** Used to get the status a node, the payload is a JSON string
- **year4000.pycloud.remove** Used to remove a node, the payload is a JSON string


## API Messaging Channel

PyCloud runs with Redis to trigger the creation of nodes from multiple servers all running PyCloud.
A service can use publish a JSON string on the channels above and one of the instances will process it.

### Create

- Request Channel `year4000.pycloud.create`
```json
{
  "id": "RANDOMLY_GENERATED_BY_USER",
  "script": "SCRIPT TO RUN ON SERVER AFTER REQUEST IS RECEIVED"
}
```

- Response Channel `year4000.pycloud.create.RANDOMLY_GENERATED_BY_USER`
```json
{
  "cloud": "PYCLOUD_HASH",
  "id": "SESSION_HASH"
}
```

### Status / Remove

At this moment both Status and Remove calls are the same Request and Response but Status grabs the status while Remove removes the node.

- Request Channel `year4000.pycloud.status`
- Request Channel `year4000.pycloud.remove`
```json
{
  "id": "RANDOMLY_GENERATED_BY_USER",
  "session": "SESSION_HASH"
}
```

- Response Channel `year4000.pycloud.status.RANDOMLY_GENERATED_BY_USER`
- Response Channel `year4000.pycloud.remove.RANDOMLY_GENERATED_BY_USER`
```json
{
  "cloud": "PYCLOUD_HASH",
  "id": "SESSION_HASH",
  "status": true
}
```
