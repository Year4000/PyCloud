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
from utils import generate_id


SESSION_DIR = '/var/run/year4000/pycloud/'


""" The session object that represents the session """
class Session:
    def __init__(self, cloud):
        self.id = generate_id()
        self.cloud = cloud


    """ Create the session """
    def create(self):
        # todo create the session environment
        print("Create session: " + self.id)


    """ Remove the session """
    def remove(self):
        # todo stop the session
        # todo remove the session files
        print("Remove session: " + self.id)


    """ Start the session """
    def start(self, script):
        # todo write the script to the session
        # todo start the tmux session
        # todo start the script
        print("Start session: " + self.id)


""" The wrapper to handle TMUX """
class Tmux:
    def __cmd(self, *command):
        subprocess.call(command)
