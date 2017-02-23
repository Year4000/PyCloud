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

""" The daemon process that manages the servers """

import os
from threading import Lock
from json import JSONEncoder
from time import time
from .session import Session
from .utils import generate_id, check_not_none
import psutil


class Cloud:
    """ The cloud instance that stores the sessions that are running """

    __inst = None

    def __init__(self):
        Cloud.__inst = self
        self.__sessions_lock = Lock()
        self.__ranks_lock = Lock()
        self.id = generate_id()
        self.__sessions = []
        self.__session_counter = 0
        self.settings = None
        self.__group = os.getenv('PYCLOUD_GROUP', 'pycloud')
        self.__ranks = set()
        self.__ranks.add(self.generate_rank())

    @staticmethod
    def get():
        """ Get the cloud instance """
        if Cloud.__inst is None:
            Cloud.__inst = Cloud()

        return Cloud.__inst

    def sessions(self):
        """ Get all the session ids that are running """
        sessions = ()

        for session in self.__sessions:
            sessions += (repr(session),)

        return sessions

    def group(self, group=None):
        """ Get or set the group for the cloud """
        if group is None:
            return self.__group
        else:
            self.__group = group

    def create_session(self, script):
        """ Create a new session from the json input """
        with self.__sessions_lock:
            session = Session(self, script)
            self.__sessions.append(session)
            self.__session_counter += 1

            session.create()
            session.start()

        return session

    def is_session(self, hash_id):
        """ Does a session exists sessions """
        session = None
        check_not_none(hash_id)

        for node in self.__sessions:
            if node.id == hash_id:
                session = node

        return session is not None

    def remove_session(self, hash_id):
        """ Remove a session from sessions """
        session = None
        check_not_none(hash_id)

        for node in self.__sessions:
            if node.id == hash_id:
                session = node

        if session is None:
            raise Exception('Session not found')

        with self.__sessions_lock:
            self.__sessions.remove(session)
            session.remove()

        return session

    def remove_ranks(self):
        """ Get the ranks and sort them """
        current_time = time() - 1
        copy_ranks = self.__ranks.copy()

        with self.__ranks_lock:
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
            raise TypeError('Rank must be a Rank type')

        with self.__ranks_lock:
            if rank not in self.__ranks:
                self.__ranks.add(rank)
            else:
                self.__ranks.remove(rank)
                self.__ranks.add(rank)

    def is_server(self):
        """ Check if this session is this session """
        ranks = self.get_ranks()

        return len(ranks) > 0 and ranks[0].id == self.id

    def generate_rank(self):
        """ Generate a rank object to send through redis """
        return Rank(cloud=self)


class Rank:
    """ The object that represents the rank of each cloud """

    def __init__(self, cloud_id=None, score=None, unix_time=None, sessions=None, cloud=None):
        if cloud is not None:
            self.id = cloud.id
            self.time = time()
            self.sessions = cloud.sessions()
            self.score = len(self.sessions) + (psutil.cpu_percent() + psutil.virtual_memory()[2]) / 2
        else:
            self.id = check_not_none(cloud_id, 'Must include cloud id')
            self.score = int(check_not_none(score, 'Must include cloud score'))
            self.time = check_not_none(unix_time, 'Must include unix time of updated')
            self.sessions = check_not_none(sessions, 'Must include the sessions the cloud is running')

    def __lt__(self, other):
        return self.score < other.score

    def __le__(self, other):
        return self.score <= other.score

    def __gt__(self, other):
        return self.score > other.score

    def __ge__(self, other):
        return self.score >= other.score

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __hash__(self):
        return int(self.id, 16)

    def __str__(self):
        return JSONEncoder().encode({
            'id': self.id,
            'score': self.score,
            'time': self.time,
            'sessions': self.sessions,
        })

    def __repr__(self):
        return 'Rank' + self.__str__()
