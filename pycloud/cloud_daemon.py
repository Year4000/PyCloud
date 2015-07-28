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
from time import time
from redis import Redis
from .redis_handler import InputMessaging, RankMessaging
from .session_manager import Session, Rank
from .utils import generate_id


class Cloud:
    """ The cloud instance that stores the sessions that are running """

    __inst = None

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

    def create_session(self):
        """ Create a new session from the json input """
        # todo add args to method
        session = Session(self)
        self.sessions.append(session)
        session.create()

    def remove_ranks(self):
        """ Get the ranks and sort them """
        current_time = time()
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

    def generate_rank(self):
        """ Generate a rank object to send through redis """
        score = len(self.sessions)
        return Rank(self.id, score, time())


def main():
    """ Deploy all the needed threads """
    cloud = Cloud.get()
    print("PyCloud ID: " + cloud.id)

    redis = Redis()
    redis_input_messaging = InputMessaging(redis)
    redis_rank_messaging = RankMessaging(cloud, redis)

    # Start in put messaging channel
    messaging = threading.Thread(target=redis_input_messaging.clock)
    messaging.setDaemon(True)
    messaging.start()

    # Start to accept rank score
    messaging = threading.Thread(target=redis_rank_messaging.clock)
    messaging.setDaemon(True)
    messaging.start()

    # Start the clock to send the rank score
    messaging = threading.Thread(target=redis_rank_messaging.send)
    messaging.setDaemon(True)
    messaging.start()

    # Keep the main thread running
    read_loop()


def read_loop():
    """ An infinant loop """

    try:
        while True:
            input("")
    except:
        print("\nEnding...")


if __name__ == '__main__':
    main()
