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
from redis import Redis
from redis_handler import InputMessaging
from session_manager import Session


class Cloud:
    """ The cloud instance that stores the sessions that are running """

    __inst = None

    def __init__(self):
        Cloud.__inst = self
        self.sessions = []

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


def main():
    """ Deploy all the needed threads """

    redis = Redis()
    redis_messaging = InputMessaging(redis)

    # Start in put messaging channel
    messaging = threading.Thread(target=redis_messaging.clock)
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
