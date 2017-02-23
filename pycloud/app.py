#!/usr/bin/python3
# Copyright 2016 Year4000.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

""" The main entry point to the system """

import threading
import sys
import logging
import os
import signal
from time import sleep
from .constants import SESSION_DIR, DATA_DIR, LOG_DIR, CONFIG_DIR, CONFIG_FILE, LOG_FILE, PID_FILE
from .handlers import CreateMessaging, StatusMessaging, RemoveMessaging, RankMessaging
from .utils import remove, default_val, required_paths
from .cloud import Cloud
from redis import Redis
from redis.exceptions import ConnectionError
import yaml


def start_daemon(nodes=None):
    """ Spins off a process that runs as a daemon """
    pid = os.fork()
    _log.info('Forked new process, pid={0}'.format(pid))

    if pid == 0:
        os.setsid()
        pid = os.fork()

        if pid == 0:
            os.chdir(SESSION_DIR)
            os.umask(0)
        else:
            sys.exit(0)
    else:
        sys.exit(0)

    if os.path.exists(PID_FILE):
        _log.info('Process is all ready running')
        sys.exit(1)

    # Set up pid_file and signal handlers.
    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(os.getpid()))

    _log.info('Send SIGABRT to shutdown daemon')
    signal.signal(signal.SIGABRT, shutdown_daemon)

    main(nodes)


def shutdown_daemon(*args):
    """ Shutdown the method to run when shutting down """
    _log.info('Shutting down PyCloud')

    # Close all running session
    for session in Cloud.get().sessions():
        Cloud.get().remove_session(session)

    if len(args) > 0:
        os.remove(PID_FILE)
        raise SystemExit('Terminating on signal number {0}'.format(args[0]))


def main(nodes=None):
    """ Deploy all the needed threads """
    nodes = int(0 if nodes is None else nodes)
    cloud = Cloud.get()
    group = cloud.group()
    _log.info('PyCloud ID: ' + cloud.id)
    _log.info('Group: ' + group)

    _log.info('Importing settings')
    with open(CONFIG_FILE, 'r') as config:
        cloud.settings = yaml.load(config)
        redis_config = cloud.settings['redis']
        host = default_val(redis_config['host'], 'localhost')
        port = default_val(redis_config['port'], 6379)
        password = redis_config['password'] if 'password' in redis_config else None

        # Only update region if not pycloud
        if cloud.settings['region'] is not None and group != cloud.settings['region']:
            cloud.group(cloud.settings['region'])
            _log.info("Group: " + group)

    _log.info('Purging old sessions')
    for folder in os.listdir(DATA_DIR):
        remove(DATA_DIR + folder)

    redis = Redis(host, port, password=password)
    redis_create_messaging = CreateMessaging(cloud, redis)
    redis_status_messaging = StatusMessaging(cloud, redis)
    redis_remove_messaging = RemoveMessaging(cloud, redis)
    redis_rank_messaging = RankMessaging(cloud, redis)

    # Make sure the connection to redis exists
    while True:
        try:
            redis.ping()
            break
        except ConnectionError:
            _log.error('Trying to connect to redis again')
            sleep(1)

    # Start the messaging channel to handle sessions
    daemon_thread(redis_create_messaging.clock, 'Create Channel')
    daemon_thread(redis_status_messaging.clock, 'Status Channel')
    daemon_thread(redis_remove_messaging.clock, 'Remove Channel')

    # Start to accept rank score
    daemon_thread(redis_rank_messaging.clock, 'Rank Input')

    # Start the clock to send the rank score
    daemon_thread(redis_rank_messaging.send, 'Rank Output')

    # Spin up test nodes for testing
    if nodes > 0:
        for i in range(0, nodes):
            cloud.create_session('#!/bin/bash\n sleep 240')

        _log.info('Test Sessions: ' + str(cloud.sessions()))

    # Keep app running
    while True:
        sleep(1)


def daemon_thread(target, name=None):
    """ Create a daemon thread with specific target """
    thread = threading.Thread(target=target)
    thread.setDaemon(True)

    if name is not None:
        thread.setName('PyCloud ' + name.title() + ' Thread')

    thread.start()
    return thread


if __name__ == '__main__':
    _log = logging.getLogger('pycloud')
    _log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    _log.addHandler(file_handler)

    # Make sure the needed folders exist
    required_paths()

    # Get the number of test nodes
    test_nodes = None
    if '--test-nodes' in sys.argv:
        pos = sys.argv.index('--test-nodes')

        if pos + 1 < len(sys.argv):
            test_nodes = sys.argv[pos + 1]

    # Start the system
    if '--daemon' in sys.argv:
        start_daemon(test_nodes)
    else:
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(formatter)
        _log.addHandler(stream_handler)

        try:
            main(test_nodes)
        except KeyboardInterrupt:
            shutdown_daemon()
