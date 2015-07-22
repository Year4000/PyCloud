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


class Messaging:
    """ Base class for listening on the redis channel """

    def __init__(self, redis, channel):
        """ Create the instances with redis """
        self.redis = redis
        self.channel = channel

    def clock(self):
        """ The method that will run for ever """
        channel = self.redis.pubsub()
        channel.subscribe(self.channel)
        
        for data in channel.listen():
            if not data['type'] == 'message':
                continue

            self.process(data)

    def process(self, data):
        """ The method that will run for ever """
        raise NotImplementedError()


class InputMessaging(Messaging):
    """ Listen to the INPUT_CHANNEL and process the node """

    def __init__(self, redis):
        """ Create the instances with redis """
        Messaging.__init__(self, redis, INPUT_CHANNEL)

    def process(self, data):
        """ The thread that runs and process the data """
        # todo process the data for tmux
        print("INPUT: " + str(data))