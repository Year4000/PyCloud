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
import sys
from pycloud.utils import install, is_root, copy, remove
from pycloud.cloud import LOG_FOLDER, CONFIG_PATH, CONFIG_FILE
from pycloud.session import SESSION_DIR, DATA_DIR
from pycloud.app import RUN_FOLDER


INSTALL_PATH = '/opt/year4000/'
REQUIREMENTS = ('tmux', 'python3-redis', 'python3-yaml', 'python3-psutil')


def main():
    """ The main function to run """
    print('INFO: Checking and installing requirements')
    for need in REQUIREMENTS:
        print(' - ', end='')
        install(need)

    def make_dir(path):
        """ Install dir path """
        try:
            os.makedirs(path)
        except OSError:
            print('NOTICE: Install path ' + path + ' exists, skipping stage')
        finally:
            os.chmod(path, 0o777)

    print('INFO: Creating install path directories')
    make_dir(INSTALL_PATH)
    make_dir(SESSION_DIR)
    make_dir(DATA_DIR)
    make_dir(LOG_FOLDER)
    make_dir(CONFIG_PATH)
    make_dir(RUN_FOLDER)

    def copy_update(old, new, can_update=False):
        """ Copy the files or folder but allow for updating """
        try:
            if '--update' in sys.argv and can_update:
                remove(new)
            elif os.path.exists(new):
                raise OSError(new)

            copy(old, new)
        except OSError:
            message = 'run again with --update' if can_update else 'you have install it yourself'
            print('ERROR: {0} installed, {1}'.format(new, message))

    print('INFO: Copying files to install path')
    copy_update('settings.yml', CONFIG_FILE)
    copy_update('pycloudd', '/etc/init.d/pycloudd', can_update=True)
    copy_update('pycloud', INSTALL_PATH + 'pycloud', can_update=True)

    print('INFO: Trying to let pycloud start at start up')
    try:
        os.system('update-rc.d pycloudd defaults')
    except OSError:
        print('ERROR: Could not run command auto you have to set it up yourself')


if __name__ == '__main__':
    """ Run the install script """
    if not is_root():
        print('ERROR: Need to run as root')
    else:
        main()
