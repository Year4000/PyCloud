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

""" The update to have PyCloud automatically download and install releases """

import os
import sys
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError
from json import JSONDecoder
from . import __version__ as version

GITHUB_RELEASES = 'https://api.github.com/repos/Year4000/PyCloud/releases'
GITHUB_COMMIT = 'https://api.github.com/repos/Year4000/PyCloud/commits'
PATH = '/tmp/pycloud-update.zip'


class UpdaterError(BaseException):
    """ Exception occurs when updater has problems """

    def __init__(self, message='', *args, **kwargs):
        self.__message = str(message).format(*args, **kwargs)

    def get_message(self):
        """ Get the formatted message of the error """
        return self.__message


class Updater:
    """ The Update class that will Update PyCloud from GitHub release """

    def __init__(self, token):
        if token is None:
            self.token = ''
        else:
            self.token = '?access_token=' + token
        self._fetch_release()
        self.downloaded = False

    def _fetch_release(self):
        """ Fetch the json object from GitHub """
        try:
            pool = PoolManager()
            header = {'User-Agent': 'Mozilla/5.0 - Year4000 PyCloud Updater'}
            response_release = pool.request('GET', GITHUB_RELEASES + self.token, headers=header)
            response_sha = pool.request('GET', GITHUB_COMMIT + self.token, headers=header)
            self.json_object = JSONDecoder().decode(response_release.data.decode('utf-8'))[0]
            self.sha = JSONDecoder().decode(response_sha.data.decode('utf-8'))[0]['sha']
        except (HTTPError, UpdaterError):
            self.json_object = {'tag_name': 'v' + version}
            self.sha = ''

    def check_for_updates(self):
        """ Check for release updates and compare with version """
        tag_name = self.json_object['tag_name'][1:6]
        need_update = version < tag_name

        print('Local Version: {0} Remote Version: {1} Update: {2}'.format(version, tag_name, need_update))
        return need_update

    def download_update(self):
        """ Download the pycloud update """
        url = self.json_object['zipball_url']

        if os.path.exists(PATH):
            os.remove(PATH)

        try:
            os.system('wget -qO {0} {1}'.format(PATH, url + self.token))
            self.downloaded = True
        except OSError as os_error:
            raise UpdaterError(str(os_error))

    def install_update(self):
        if not os.path.exists(PATH) and self.downloaded:
            raise UpdaterError('Install zip does not exist')

        try:
            os.system('cd /tmp/ ; unzip {} -d /tmp/PyCloud-{}'.format(PATH, self.sha))
            os.system('/tmp/PyCloud-{}/*/install.py --update'.format(self.sha))
        except OSError as os_error:
            raise UpdaterError(str(os_error))


def main(force=False, token=''):
    """ Run the Updater """
    updater = Updater(token)

    if updater.check_for_updates() or force:
        try:
            updater.download_update()
        except UpdaterError as error:
            print('Fail to download update... ' + error.get_message())

        try:
            updater.install_update()
        except UpdaterError as error:
            print('Fail to install update... ' + error.get_message())


if __name__ == '__main__':
    access_token = None

    if '--token' in sys.argv:
        pos = sys.argv.index('--token')

        if pos + 1 < len(sys.argv):
            access_token = sys.argv[pos + 1]

    main('--force' in sys.argv, access_token)
