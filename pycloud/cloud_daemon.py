#!/usr/bin/python3
# Copyright 2015 Year4000.
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

""" The daemon process that manages the servers """

import threading
import logging
import sys
import os
import datetime
from time import time
from redis import Redis
from .handlers import CreateMessaging, StatusMessaging, RemoveMessaging, RankMessaging
from .managers import Session, Rank, DATA_DIR
from .utils import generate_id, remove, check_not_none


LOG_FOLDER = '/var/log/year4000/pycloud/'
FILE_LOG = LOG_FOLDER + str(datetime.date.today()) + ".log"


class Cloud:
    """ The cloud instance that stores the sessions that are running """

    __inst = None
    __group = os.getenv("PYCLOUD_GROUP", "pycloud")

    def __init__(self):
        Cloud.__inst = self
        self.id = generate_id()
        self.sessions = []
        self.__ranks = set()
        self.__ranks.add(self.generate_rank())

    @staticmethod
    def get():
        """ Get the cloud instance """
        if Cloud.__inst is None:
            Cloud.__inst = Cloud()

        return Cloud.__inst

    def create_session(self, script):
        """ Create a new session from the json input """
        session = Session(self, script)
        self.sessions.append(session)
        session.create()
        session.start()
        return session

    def is_session(self, hash_id):
        """ Does a session exists sessions """
        session = None
        check_not_none(hash_id)

        for node in self.sessions:
            if node.id == hash_id:
                session = node

        return session is None

    def remove_session(self, hash_id):
        """ Remove a session from sessions """
        session = None
        check_not_none(hash_id)

        for node in self.sessions:
            if node.id == hash_id:
                session = node

        if session is None:
            raise Exception('Session not found')

        self.sessions.remove(session)
        session.remove()
        return session

    def remove_ranks(self):
        """ Get the ranks and sort them """
        current_time = time() - 1
        copy_ranks = self.__ranks.copy()

        for rank in copy_ranks:
            if rank.time < current_time:
                self.__ranks.remove(rank)

    def get_ranks(self):
        """ Remove outdated ranks """
        ranks = []

        for rank in self.__ranks:
            if rank not in ranks:
                ranks.append(rank)

        ranks.sort()

        return ranks

    def add_rank(self, rank):
        """ Add the rank to the ranks list """

        if not isinstance(rank, Rank):
            raise TypeError("Rank must be a Rank type")

        if rank not in self.__ranks:
            self.__ranks.add(rank)
        else:
            self.__ranks.remove(rank)
            self.__ranks.add(rank)

    def is_server(self):
        """ Check if this session is this session """
        ranks = self.get_ranks()

        return ranks[len(ranks) - 1].id == self.id

    def generate_rank(self):
        """ Generate a rank object to send through redis """
        score = len(self.sessions)
        return Rank(self.id, score, time())


def main():
    """ Deploy all the needed threads """
    cloud = Cloud.get()
    _log.info("PyCloud ID: " + cloud.id)
    _log.info("Group: " + Cloud._Cloud__group)

    _log.info("Purging old sessions")
    for folder in os.listdir(DATA_DIR):
        remove(DATA_DIR + folder)

    redis = Redis()
    redis_create_messaging = CreateMessaging(cloud, redis)
    redis_status_messaging = StatusMessaging(cloud, redis)
    redis_remove_messaging = RemoveMessaging(cloud, redis)
    redis_rank_messaging = RankMessaging(cloud, redis)

    # Start the messaging channel to handle sessions
    daemon_thread(redis_create_messaging.clock, "Create Channel")
    daemon_thread(redis_status_messaging.clock, "Status Channel")
    daemon_thread(redis_remove_messaging.clock, "Remove Channel")

    # Start to accept rank score
    daemon_thread(redis_rank_messaging.clock, "Rank Input")

    # Start the clock to send the rank score
    daemon_thread(redis_rank_messaging.send, "Rank Output")

    # Keep the main thread running
    read_loop()


def daemon_thread(target, name=None):
    """ Create a daemon thread with specific target """
    thread = threading.Thread(target=target)
    thread.setDaemon(True)

    if name is not None:
        thread.setName("PyCloud " + name.title() + " Thread")

    thread.start()
    return thread


def read_loop():
    """ An infinant loop """

    try:
        while True:
            input("")
    except KeyboardInterrupt:
        _log.info("Ending...")


if __name__ == '__main__':
    _log = logging.getLogger("pycloud")
    _log.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(FILE_LOG)
    file_handler.setFormatter(formatter)
    _log.addHandler(stream_handler)
    _log.addHandler(file_handler)

    main()
