# PyCloud

A python wrapper daemon that manages tmux sessions
and provides a json control over the sessions
with redis messaging channels.

## Installation

Run the python script `install.py`. When updating make sure to remove old paths.

## Updating

The system will try its best to self update with the update command. This works by using GitHub's Releases provided in the git repo.
- Run `pycloudd update` to trigger the update checker.
- Use `pycloudd update --force` to force an update of the current version.

## Daemon Script

When installing there is a daemon script that is a wrapper for the commands bellow.

## Running

In single session mode
> python3 -m pycloud.app

In system daemon mode
> python3 -m pycloud.app --daemon

## Redis Channels

- **year4000.pycloud.rank** Used for internal tracking of servers
- **year4000.pycloud.create** Used to create a node, the payload is a JSON string
- **year4000.pycloud.status** Used to get the status a node, the payload is a JSON string
- **year4000.pycloud.remove** Used to remove a node, the payload is a JSON string
