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

""" Wrapper to create tmux sessions """

import subprocess
from json import JSONEncoder
from .utils import generate_id


SESSION_DIR = '/var/run/year4000/pycloud/'


class Rank:
    """ The object that represents the rank of each object """

    def __init__(self, id, score, time):
        self.id = id
        self.score = int(score)
        self.time = time

    __lt__ = lambda self, other: self.score < other.score
    __le__ = lambda self, other: self.score <= other.score
    __gt__ = lambda self, other: self.score > other.score
    __ge__ = lambda self, other: self.score >= other.score
    __eq__ = lambda self, other: self.id == other.id
    __ne__ = lambda self, other: self.id != other.id
    __hash__ = lambda self: int(self.id, 16)

    def __str__(self):
        return JSONEncoder().encode({'id': self.id, 'score': self.score, 'time': self.time})

    def __repr__(self):
        return "Rank" + self.__str__()


class Session:
    """ The session object that represents the session """

    def __init__(self, cloud):
        """ Generate this session with the cloud instance """
        self.id = generate_id()
        self.cloud = cloud

    def create(self):
        """ Create the session """
        # todo create the session environment
        print("Create session: " + self.id)

    def remove(self):
        """ Remove the session """
        # todo stop the session
        # todo remove the session files
        print("Remove session: " + self.id)

    def start(self, script):
        """ Start the session """
        # todo write the script to the session
        # todo start the tmux session
        # todo start the script
        print("Start session: " + self.id)


class Tmux:
    """ The wrapper to handle TMUX """

    def __cmd(self, *command):
        subprocess.call(command)
