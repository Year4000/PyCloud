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

""" Utilities to aid with the cloud system """

import os
import sys
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


def remove(path):
    """ Remove a folder and all its contents """
    max_checks = 10
    checks = 0

    while os.path.exists(path):
        if checks > max_checks:
            break

        try:
            shutil.rmtree(check_not_none(path))
        except OSError:
            break


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


def check_not_none(var, message='Var is None'):
    """ Check that the var is not none """
    if var is None:
        raise ValueError(message)

    return var


def default_val(var, default):
    """ If var is None assign default value """
    if var is None:
        var = default

    return var

def copy_update(old, new, can_update=False):
    """ Copy the files or folder but allow for updating """
    try:
        if '--update' in sys.argv and can_update:
            remove(new)
        elif os.path.exists(new):
            raise OSError(new)

        copy(old, new)
    except OSError:
        message = 'run again with --update' if can_update else 'you have update it yourself'
        print('ERROR: {0} installed, {1}'.format(new, message))
