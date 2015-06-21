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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Utilities to aid with the cloud system """

import os
import subprocess

FNULL=open(os.devnull, 'w')

""" Check if their is output if not install it """
def install(name):
    FNULL = open(os.devnull, 'w')
    out = subprocess.call(['dpkg', '-s', name], stdout=FNULL, stderr=FNULL)

    if out == 0:
        print('Installed ' + name)
    else:
        print('Installing ' + name)
        subprocess.call(['apt-get', 'install', '-y', name], stdout=FNULL, stderr=FNULL)


""" Make sure current user is root """
def is_root():
    return os.getuid() == 0

