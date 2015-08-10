# PyCloud

A python wrapper daemon that manages tmux sessions
and provides a json control over the sessions
with redis messaging channels.

## Installation

Run the python script `install.py`


## Running

In single session mode
> python3 -m pycloud.cloud_daemon

In system daemon mode
> tmux new -s PyCloud -n PyCloud -d 'python3 -m pycloud.cloud_daemon'

## Redis Channels

- **year4000.pycloud.rank** Used for internal tracking of servers
- **year4000.pycloud.create** Used to create a node, the payload is a JSON string
- **year4000.pycloud.status** Used to get the status a node, the payload is a JSON string
- **year4000.pycloud.remove** Used to remove a node, the payload is a JSON string
