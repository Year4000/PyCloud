# PyCloud

A python wrapper daemon that manages tmux sessions
and provides a json control over the sessions
with redis messaging channels.

## Installation

Run the python script `install.py`


## Running

> python3 -m pycloud.cloud_daemon

## Redis Channels

**year4000.pycloud.rank** Used for internal tracking of servers
**year4000.pycloud.input** Used to create or destroy a node, the payload is a JSON string
