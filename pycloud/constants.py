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

""" Constants needed for the program and setuptools """

import datetime

RUN_FOLDER = '/var/run/year4000/pycloud/'
PID_FILE = RUN_FOLDER + 'pycloud.pid'

CONFIG_PATH = '/etc/year4000/pycloud/'
CONFIG_FILE = CONFIG_PATH + 'settings.yml'
LOG_FOLDER = '/var/log/year4000/pycloud/'
FILE_LOG = LOG_FOLDER + str(datetime.date.today()) + ".log"

CREATE_CHANNEL = 'year4000.pycloud.create'
STATUS_CHANNEL = 'year4000.pycloud.status'
REMOVE_CHANNEL = 'year4000.pycloud.remove'
RANK_CHANNEL = 'year4000.pycloud.rank'

SESSION_DIR = '/var/run/year4000/pycloud/'
DATA_DIR = '/var/lib/year4000/pycloud/'
