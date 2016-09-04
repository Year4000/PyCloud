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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from pycloud.utils import install, is_root, copy_update, required_paths
from pycloud.constants import CONFIG_FILE
from pycloud import __version__
from setuptools import setup, find_packages

# Must be ran as root
if not is_root():
    print('ERROR: Need to run as root')
    sys.exit(1)

print('INFO: Checking and installing requirements')
install('tmux')
os.system('! id year4000 && useradd year4000 -M -s /usr/sbin/nologin -u 4000')

print('INFO: Copying files to install path')
copy_update('settings.yml', CONFIG_FILE)
copy_update('pycloudd', '/etc/init.d/pycloudd', can_update=True)
required_paths()

print('INFO: Trying to let pycloud start at start up')
try:
    os.system('update-rc.d pycloudd defaults')
except OSError:
    print('ERROR: Could not run command auto you have to set it up yourself')

# Run the needed things from pip
setup(
    name='pycloud',
    version=__version__,
    description='Manages the PyCloud daemon by providing wrapper for common PyCloud tasks',
    author='Year4000',
    url='https://github.com/Year4000/PyCloud',
    install_requires=['redis', 'PyYAML', 'psutil'],
    packages = find_packages(),
)
