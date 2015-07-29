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
import datetime
from time import time
from redis import Redis
from .redis_handler import InputMessaging, RankMessaging
from .session_manager import Session, Rank
from .utils import generate_id


FILE_LOG = "/var/log/pycloud/" + str(datetime.date.today()) + ".log"

_log = logging.getLogger("pycloud")
_log.setLevel(logging.INFO)
_log.addHandler(logging.StreamHandler(stream=sys.stdout))
_log.addHandler(logging.FileHandler(FILE_LOG))


class Cloud:
    """ The cloud instance that stores the sessions that are running """

    _inst = None

    def __init__(self):
        Cloud._inst = self
        self.id = generate_id()
        self.sessions = []
        self._ranks = set()
        self._ranks.add(self.generate_rank())

    @staticmethod
    def get():
        """ Get the cloud instance """
        if Cloud._inst is None:
            Cloud._inst = Cloud()

        return Cloud._inst

    def create_session(self):
        """ Create a new session from the json input """
        # todo add args to method
        session = Session(self)
        self.sessions.append(session)
        session.create()

    def remove_ranks(self):
        """ Get the ranks and sort them """
        current_time = time() - 1
        copy_ranks = self._ranks.copy()

        for rank in copy_ranks:
            if rank.time < current_time:
                self._ranks.remove(rank)

    def get_ranks(self):
        """ Remove outdated ranks """
        ranks = []

        for rank in self._ranks:
            if rank not in ranks:
                ranks.append(rank)

        ranks.sort()

        return ranks

    def add_rank(self, rank):
        """ Add the rank to the ranks list """

        if not isinstance(rank, Rank):
            raise TypeError("Rank must be a Rank type")

        if rank not in self._ranks:
            self._ranks.add(rank)
        else:
            self._ranks.remove(rank)
            self._ranks.add(rank)

    def generate_rank(self):
        """ Generate a rank object to send through redis """
        score = len(self.sessions)
        return Rank(self.id, score, time())


def main():
    """ Deploy all the needed threads """
    cloud = Cloud.get()
    _log.info("PyCloud ID: " + cloud.id)

    redis = Redis()
    redis_input_messaging = InputMessaging(redis)
    redis_rank_messaging = RankMessaging(cloud, redis)

    # Start in put messaging channel
    daemon_thread(redis_input_messaging.clock, "Input Channel")

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
    except:
        _log.info("\nEnding...")


if __name__ == '__main__':
    main()
