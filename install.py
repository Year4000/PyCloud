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

import os
from pycloud.utils import install
from pycloud.utils import is_root
from pycloud.utils import copy


INSTALL_PATH = '/opt/year4000/'
LOG_FOLDER = '/var/log/pycloud/'
REQUIREMENTS = ('tmux', 'python3-redis')


def main():
    """ The main function to run """
    global REQUIREMENTS

    print('INFO: Checking and installing requirements')
    for need in REQUIREMENTS:
        print(' - ', end='')
        install(need)

    print('INFO: Creating install path directories')
    try:
        os.makedirs(INSTALL_PATH)
        os.makedirs(LOG_FOLDER)
    except:
        print('NOTICE: Install path ' + INSTALL_PATH + ' exists, skipping stage')

    print('INFO: Copying files to install path')
    try:
        copy('pycloud', INSTALL_PATH + 'pycloud')
    except:
        print('ERROR: PyCloud is already installed, remove ' + INSTALL_PATH + 'pycloud')


if __name__ == '__main__':
    """ Run the install script """
    if not is_root():
        print('ERROR: Need to run as root')
    else:
        main()
