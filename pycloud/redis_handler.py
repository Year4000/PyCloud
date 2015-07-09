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

""" The redis handler that will handle the PubSub channel """

INPUT_CHANNEL = "year4000.pycloud.input"


""" Listen to the INPUT_CHANNEL and process the node """
class InputMessaging:

    """ Create the instances with redis """
    def __init__(self, redis):
        self.redis = redis


    """ The thread that runs and process the data """
    def clock(self):
        channel = self.redis.pubsub()
        channel.subscribe(INPUT_CHANNEL)
        
        for data in channel.listen():
            if not data['type'] == 'message': continue

            # todo process the data for tmux
            print("INPUT: " + str(data))