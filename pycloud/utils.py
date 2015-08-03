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

""" Utilities to aid with the cloud system """

import os
import subprocess
import shutil
import time
import random


FNULL = open(os.devnull, 'w')


def install(name):
    """ Check if their is output if not install it """
    out = subprocess.call(['dpkg', '-s', name], stdout=FNULL, stderr=FNULL)

    if out == 0:
        print('Installed ' + name)
    else:
        print('Installing ' + name)
        subprocess.call(['apt-get', 'install', '-y', name], stdout=FNULL, stderr=FNULL)


def is_root():
    """ Make sure current user is root """
    return os.getuid() == 0


def remove(path=None, parent=None, child=None):
    """ Remove a folder and all its contents """
    if path is not None and os.path.isdir(path):
        for content in os.listdir(path):
            remove(path + "/" + content, parent=path, child=content)
    elif parent is not None and child is not None:
        os.chdir(parent)
        if os.path.isdir(child):
            os.rmdir(child)
        else:
            os.remove(child)


def copy(in_path, out_path):
    """ Copy a directory or file to path """
    if os.path.isdir(in_path):
        shutil.copytree(in_path, out_path)
    else:
        shutil.copy(in_path, out_path)


def generate_id():
    """ Create an id to use to identify processes """
    random_number = int(random.random() * 0xFFFFFF)
    system_time = int(time.time())
    process_id = os.getpid()

    return hex(random_number + process_id + system_time)[2:]