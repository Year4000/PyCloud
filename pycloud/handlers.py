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
from .cloud import Rank
from .utils import check_not_none

try:
    from redis.exceptions import RedisError
except ImportError:
    if __name__ == "__main__":
        print('Fail to import, make sure to run ./install.py first')
        sys.exit(1)

_log = logging.getLogger('pycloud')
CREATE_CHANNEL = 'year4000.pycloud.create'
STATUS_CHANNEL = 'year4000.pycloud.status'
REMOVE_CHANNEL = 'year4000.pycloud.remove'
RANK_CHANNEL = 'year4000.pycloud.rank'


class Messaging:
    """ Base class for listening on the redis channel """

    def __init__(self, redis, channel):
        """ Create the instances with redis """
        self._redis = redis
        self._channel = channel
        self.__error = None

    def clock(self):
        """ The method that will run for ever """
        while threading.current_thread().is_alive():
            try:
                channel = self._redis.pubsub()
                channel.subscribe(self._channel)

                if self.__error is not None:
                    self.__error = False

                for data in channel.listen():
                    if self.__error is not None and not self.__error:
                        _log.error(threading.current_thread().getName() + ": Redis error fixed")
                        self.__error = None

                    if not data['type'] == 'message':
                        continue

                    try:
                        self.process(data['data'])
                    except Exception as error:
                        _log.error("Exception while processing data: " + str(error))
            except RedisError:
                self.__error = True
                _log.error(threading.current_thread().getName() + ": Redis error, trying again in 5 secs")
                sleep(5)

    def process(self, data):
        """ The method that will be called when processing the data """
        raise NotImplementedError()


class CreateMessaging(Messaging):
    """ Listen to the CREATE_CHANNEL and create the session """

    def __init__(self, cloud, redis):
        """ Create the instances with redis and cloud """
        Messaging.__init__(self, redis, CREATE_CHANNEL)
        self.__cloud = cloud

    def process(self, data):
        """ The thread that runs and create the session based on the data """
        json = JSONDecoder().decode(data.decode('utf-8'))

        try:
            hash_id = check_not_none(json['id'])
            script = check_not_none(json['script'])

            if self.__cloud.is_server():
                sleep(0.25)
                session = self.__cloud.create_session(script)
                results = {'cloud': self.__cloud.id, 'id': session.id}
                self._redis.publish(CREATE_CHANNEL + '.' + hash_id, str(results))
        except ValueError as error:
            _log.error('Input error: ' + str(error))


class RemoveMessaging(Messaging):
    """ Listen to the REMOVE_CHANNEL and remove the session """

    def __init__(self, cloud, redis):
        """ Create the instances with redis and cloud """
        Messaging.__init__(self, redis, REMOVE_CHANNEL)
        self.__cloud = cloud

    def process(self, data):
        """ The thread that runs and remove the session """
        json = JSONDecoder().decode(data.decode('utf-8'))

        try:
            hash_id = check_not_none(json['id'])
            session = check_not_none(json['session'])
            status = self.__cloud.is_session(session)

            if status:
                self.__cloud.remove_session(session)

            if status or (not status and self.__cloud.is_server()):
                sleep(0.25)
                results = {'cloud': self.__cloud.id, 'session': session, 'status': status}
                self._redis.publish(REMOVE_CHANNEL + '.' + hash_id, str(results))
        except ValueError as error:
            _log.error('Remove error: ' + str(error))


class StatusMessaging(Messaging):
    """ Listen to the STATUS_CHANNEL and status the session """

    def __init__(self, cloud, redis):
        """ Create the instances with redis and cloud """
        Messaging.__init__(self, redis, STATUS_CHANNEL)
        self.__cloud = cloud

    def process(self, data):
        """ The thread that runs and gets the status of the session """
        json = JSONDecoder().decode(data.decode('utf-8'))

        try:
            hash_id = check_not_none(json['id'])
            session = check_not_none(json['session'])
            status = self.__cloud.is_session(session)

            if status or (not status and self.__cloud.is_server()):
                sleep(0.25)
                results = {'cloud': self.__cloud.id, 'id': session, 'status': status}
                self._redis.publish(STATUS_CHANNEL + '.' + hash_id, str(results))
        except ValueError as error:
            _log.error('Status error: ' + str(error))


class RankMessaging(Messaging):
    """ Listen to the RANK_CHANNEL and process the node """

    def __init__(self, cloud, redis):
        """ Create the instances with redis and cloud """
        Messaging.__init__(self, redis, RANK_CHANNEL)
        self.__cloud = cloud
        self.__error = None

    def process(self, data):
        """ The thread that runs and process the rank score """
        json = JSONDecoder().decode(data.decode('utf-8'))
        rank = Rank(json['id'], json['score'], json['time'], json['sessions'])
        self.__cloud.add_rank(rank)
        _log.debug('Cloud Nodes: ' + str(self.__cloud.get_ranks()))

    def send(self):
        """ Send the score to the other instances """
        while threading.current_thread().is_alive():
            # Remove outdated ranks
            self.__cloud.remove_ranks()

            # Send rank
            try:
                json = str(self.__cloud.generate_rank())
                self._redis.publish(self._channel, json)

                if self.__error is not None:
                    self.__error = False

                if self.__error is not None and not self.__error:
                    _log.error(threading.current_thread().getName() + ": Redis error fixed")
                    self.__error = None
            except RedisError:
                self.__error = True
                _log.error(threading.current_thread().getName() + ": Redis error, trying again in 5 secs")
                sleep(4.5)
            finally:
                sleep(0.5)
