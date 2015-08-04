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

from time import sleep
from json import JSONDecoder
import threading
import logging
from .session_manager import Rank
from .utils import check_not_none

_log = logging.getLogger('pycloud')
CREATE_CHANNEL = "year4000.pycloud.create"
STATUS_CHANNEL = "year4000.pycloud.status"
REMOVE_CHANNEL = "year4000.pycloud.remove"
RANK_CHANNEL = "year4000.pycloud.rank"


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

            self.process(data['data'])

    def process(self, data):
        """ The method that will be called when processing the data """
        raise NotImplementedError()


class CreateMessaging(Messaging):
    """ Listen to the CREATE_CHANNEL and create the session """

    def __init__(self, cloud, redis):
        """ Create the instances with redis and cloud """
        Messaging.__init__(self, redis, CREATE_CHANNEL)
        self.cloud = cloud

    def process(self, data):
        """ The thread that runs and create the session based on the data """
        json = JSONDecoder().decode(data.decode('utf-8'))

        try:
            hash_id = check_not_none(json['id'])
            script = check_not_none(json['script'])

            session = self.cloud.create_session(script)
            results = {'id': session.id}
            self.redis.publish(CREATE_CHANNEL + '.' + hash_id, str(results))
        except ValueError as error:
            _log.info('Input error: ' + str(error))


class RemoveMessaging(Messaging):
    """ Listen to the REMOVE_CHANNEL and remove the session """

    def __init__(self, cloud, redis):
        """ Create the instances with redis and cloud """
        Messaging.__init__(self, redis, REMOVE_CHANNEL)
        self.cloud = cloud

    def process(self, data):
        """ The thread that runs and remove the session """
        json = JSONDecoder().decode(data.decode('utf-8'))

        try:
            hash_id = check_not_none(json['id'])
            session = check_not_none(json['session'])
            status = self.cloud.is_session(session)

            if status:
                self.cloud.remove_session(session)

            results = {'session': session, 'status': status}
            self.redis.publish(REMOVE_CHANNEL + '.' + hash_id, str(results))
        except ValueError as error:
            _log.info('Remove error: ' + str(error))


class StatusMessaging(Messaging):
    """ Listen to the STATUS_CHANNEL and status the session """

    def __init__(self, cloud, redis):
        """ Create the instances with redis and cloud """
        Messaging.__init__(self, redis, CREATE_CHANNEL)
        self.cloud = cloud

    def process(self, data):
        """ The thread that runs and gets the status of the session """
        json = JSONDecoder().decode(data.decode('utf-8'))

        try:
            hash_id = check_not_none(json['id'])
            session = check_not_none(json['session'])

            results = {'id': session, 'status': self.cloud.is_session(session)}
            self.redis.publish(STATUS_CHANNEL + '.' + hash_id, str(results))
        except ValueError as error:
            _log.info('Status error: ' + str(error))


class RankMessaging(Messaging):
    """ Listen to the RANK_CHANNEL and process the node """

    def __init__(self, cloud, redis):
        """ Create the instances with redis and cloud """
        Messaging.__init__(self, redis, RANK_CHANNEL)
        self.cloud = cloud

    def process(self, data):
        """ The thread that runs and process the rank score """
        json = JSONDecoder().decode(data.decode('utf-8'))
        rank = Rank(json['id'], json['score'], json['time'])
        self.cloud.add_rank(rank)
        _log.debug('Cloud Nodes: ' + str(self.cloud.get_ranks()))

    def send(self):
        """ Send the score to the other instances """
        while threading.current_thread().is_alive():
            # Remove outdated ranks
            self.cloud.remove_ranks()

            # Send rank
            json = str(self.cloud.generate_rank())
            self.redis.publish(self.channel, json)
            sleep(0.25)
