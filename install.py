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

from pycloud.utils import install
from pycloud.utils import is_root


REQUIREMENTS=('tmux', 'python-redis')


""" The main function to run """
def main():
    global REQUIREMENTS

    print('Checking and installing requirements')
    for need in REQUIREMENTS:
        install(need)


""" Run the install script """ 
if __name__ == '__main__':
    if not is_root():
        print('Error: Need to run as root')
    else:
        main()
