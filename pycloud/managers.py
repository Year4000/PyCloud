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
import os
import logging
from json import JSONEncoder
from .utils import check_not_none, generate_id, remove


_log = logging.getLogger("pycloud")
SESSION_DIR = '/var/run/year4000/pycloud/'
DATA_DIR = '/var/lib/year4000/pycloud/'


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

    def __init__(self, cloud, script):
        """ Generate this session with the cloud instance """
        self.id = generate_id()
        self.cloud = check_not_none(cloud)
        self.script = check_not_none(script)
        self.session_dir = DATA_DIR + self.id + "/"
        self.session_script = self.session_dir + "pycloud.init"

    def create(self):
        """ Create the session """
        _log.info("Create session: " + self.id)

        try:
            os.makedirs(self.session_dir)
        except OSError:
            _log.error("Fail to create directory for: " + str(self))
            raise

        with open(self.session_script, 'w') as file:
            for line in self.script.split('\n'):
                print(line, file=file)

        os.chdir(self.session_dir)
        os.chmod(self.session_script, 0o777)

    def remove(self):
        """ Remove the session """
        _log.info("Remove session: " + self.id)
        Tmux(self.id).remove()
        remove(self.session_dir)

    def start(self):
        """ Start the session """
        _log.info("Start session: " + self.id)
        Tmux(self.id).create(self.session_script)


class Tmux:
    """ The wrapper to handle TMUX """

    def __init__(self, session, name='PyCloud'):
        self.session = check_not_none(session)
        self.name = name

    @staticmethod
    def __cmd(command):
        try:
            args = ('tmux',) + tuple(command)
            subprocess.call(args)
        except:
            _log.info('Could not process tmux cmd')
            raise

    def create(self, cmd=None):
        """ Create a new tmux session """
        args = ('new', '-s', self.session, '-n', self.name)

        if cmd is not None:
            args += ('-d', cmd)

        Tmux.__cmd(args)

    def remove(self):
        """ Remove tmux session """
        args = ('kill-session', '-t', self.session)
        Tmux.__cmd(args)
