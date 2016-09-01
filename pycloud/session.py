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

""" Wrapper to create tmux sessions """

import subprocess
import os
import logging
import socket
from json import JSONEncoder
from .constants import SESSION_DIR, DATA_DIR
from .utils import check_not_none, generate_id, remove, default_val


_log = logging.getLogger('pycloud')


class Session:
    """ The session object that represents the session """

    def __init__(self, cloud, script):
        """ Generate this session with the cloud instance """
        self.id = generate_id()
        self.__pid = -1
        self.__cloud = check_not_none(cloud)
        self.__script = check_not_none(script)
        self._session_dir = DATA_DIR + self.id + '/'
        self._session_script = self._session_dir + 'pycloud.init'
        self._session_config = self._session_dir + 'pycloud.json'

        # Grab an ephemeral port to use, if failed use port 0
        try:
            with socket.socket() as connection:
                connection.bind(('', 0))
                self._port = connection.getsockname()[1]
        except OSError:
            self._port = 0

    def create(self):
        """ Create the session """
        _log.info('Create session: ' + repr(self))

        try:
            os.makedirs(self._session_dir)
        except OSError:
            _log.error('Fail to create directory for: ' + str(self))
            raise

        with open(self._session_script, 'w') as file:
            for line in self.__script.split('\n'):
                print(line, file=file)

        os.chdir(self._session_dir)
        os.chmod(self._session_script, 0o777)

    def remove(self):
        """ Remove the session """
        _log.info('Remove session: ' + repr(self))
        Session.Tmux(self.id).remove()

        if self.pid > 0:
            try:
                subprocess.call("kill -9 " + str(self.pid))
            except FileNotFoundError:
                # Process is not running
                pass

        remove(self._session_dir)

    def start(self):
        """ Start the session """
        with open(self._session_config, 'w') as file:
            pretty = JSONEncoder(indent=4, separators=[',', ': ']).encode({
                'hostname': default_val(self.__cloud.settings['hostname'], socket.gethostname()),
                'port': self._port,
                'sessions': len(self.__cloud.sessions()),
            })
            print(pretty, file=file)

        self.pid = Session.Tmux(self.id).create(self._session_script)
        _log.info('Starting session: ' + str(self))

    def __repr__(self):
        """ Use the session id to represent this session """
        return self.id

    def __str__(self):
        """ Print out the id pid and port of this session """
        return "id: {0}, pid: {1}, port: {2}".format(self.id, self.pid, self._port)

    class Tmux:
        """ The wrapper to handle TMUX """

        def __init__(self, session, name='PyCloud'):
            self.session = check_not_none(session)
            self.name = name

        @staticmethod
        def __cmd(command):
            try:
                args = ('tmux',) + tuple(command)
                return subprocess.Popen(args)
            except:
                _log.info('Could not process tmux cmd')
                raise

        def create(self, cmd=None):
            """ Create a new tmux session """
            args = ('new', '-s', self.session, '-n', self.name)

            if cmd is not None:
                args += ('-d', cmd)

            return Session.Tmux.__cmd(args).pid

        def remove(self):
            """ Remove tmux session """
            args = ('kill-session', '-t', self.session)
            return Session.Tmux.__cmd(args).pid
