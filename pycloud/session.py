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
import socket
from json import JSONEncoder
from .utils import check_not_none, generate_id, remove, default_val


_log = logging.getLogger('pycloud')
SESSION_DIR = '/var/run/year4000/pycloud/'
DATA_DIR = '/var/lib/year4000/pycloud/'
PORT_RANGE = '/proc/sys/net/ipv4/ip_local_port_range'


class Session:
    """ The session object that represents the session """

    __port_counter = 0
    __ports = []

    def __init__(self, cloud, script):
        """ Generate this session with the cloud instance """
        self.id = generate_id()
        self.cloud = check_not_none(cloud)
        self.script = check_not_none(script)
        self.session_dir = DATA_DIR + self.id + '/'
        self.session_script = self.session_dir + 'pycloud.init'
        self.session_config = self.session_dir + 'pycloud.json'

        # Read port range file
        if len(Session.__ports) == 0:
            with open(PORT_RANGE, 'r') as port_range:
                ports = port_range.read().split()
                min_port = int(ports[0])
                max_port = int(ports[1])

            Session.__ports = range(min_port, max_port)

        while True:
            Session.__port_counter = 0 if Session.__port_counter >= len(Session.__ports) else Session.__port_counter
            self.port = Session.__ports[Session.__port_counter]

            try:
                # Try to connect to the port
                with socket.socket() as connection:
                    connection.connect(('', self.port))

            except ConnectionRefusedError:
                break
            finally:
                # All ways increment port counter
                Session.__port_counter += 1

    def create(self):
        """ Create the session """
        _log.info('Create session: ' + self.id)

        try:
            os.makedirs(self.session_dir)
        except OSError:
            _log.error('Fail to create directory for: ' + str(self))
            raise

        with open(self.session_script, 'w') as file:
            for line in self.script.split('\n'):
                print(line, file=file)

        os.chdir(self.session_dir)
        os.chmod(self.session_script, 0o777)

    def remove(self):
        """ Remove the session """
        _log.info('Remove session: ' + self.id)
        Session.Tmux(self.id).remove()
        remove(self.session_dir)

    def start(self):
        """ Start the session """
        _log.info('Start session: ' + self.id)

        with open(self.session_config, 'w') as file:
            pretty = JSONEncoder(indent=4, separators=[',', ': ']).encode({
                'hostname': default_val(self.cloud.settings['hostname'], socket.gethostname()),
                'port': self.port,
                'sessions': len(self.cloud.sessions()),
            })
            print(pretty, file=file)

        Session.Tmux(self.id).create(self.session_script)

    def __repr__(self):
        """ Use the session id to represent this session """
        return self.id

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

            Session.Tmux.__cmd(args)

        def remove(self):
            """ Remove tmux session """
            args = ('kill-session', '-t', self.session)
            Session.Tmux.__cmd(args)
