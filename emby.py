import logging
import time
import urllib.parse

from datamodel import UnifiedData
import httpclient
import settings


EMBY_ROOT_URL = settings.EmbyConfig.EMBY_ROOT_URL
EMBY_CLIENT = 'MediaScreen'
EMBY_DEVICE = 'RPi4'
EMBY_DEVICE_ID = 'MediaScreen'
EMBY_DEVICE_VERSION = '1.0'
EMBY_HEADERS_AUTH = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Emby-Authorization': 'Emby Client="{client}", Device="{device}", DeviceId="{device_id}", Version="{version}"'.format(
        client=EMBY_CLIENT,
        device=EMBY_DEVICE,
        device_id=EMBY_DEVICE_ID,
        version=EMBY_DEVICE_VERSION)
}
EMBY_URL_AUTH = "{root}/emby/Users/AuthenticateByName".format(root=EMBY_ROOT_URL)
EMBY_URL_SESSIONS = "{root}/emby/Sessions".format(root=EMBY_ROOT_URL)



_LOGGER = logging.getLogger(__name__)



class Emby(object):
    def __init__(self):
        self.enabled = settings.GlobalConfig.ENABLE_EMBY
        if self.enabled:
            _LOGGER.debug('Using Emby URL [{url}]'.format(url=EMBY_ROOT_URL))
            self.polling_interval = settings.EmbyConfig.EMBY_POLLING_INTERVAL
            self.last_update = time.time() - 10*self.polling_interval
            self.data = None
            self.enrichment_required = True
            self.access_token = None
            self._authenticate()

    def _authenticate(self):
        _LOGGER.debug('Authenticating to Emby URL')
        auth_data = {
            "username": settings.EmbyConfig.EMBY_USER,
            "pw": settings.EmbyConfig.EMBY_PWD
        }
        requestobj = urllib.request.Request(EMBY_URL_AUTH, data=auth_data, headers=EMBY_HEADERS_AUTH)
        obj = httpclient.get_json_from_url(requestobj)
        self.access_token = obj['AccessToken']


    async def refresh(self):
        self.last_update = time.time()
        data = self._get_nowplaying()
        self.enrichment_required = (data != self.data)
        self.data = data
        return data

    def _get_nowplaying(self):
        headers = {
            'X-Emby-Token': self.access_token
        }
        requestobj = urllib.request.Request(EMBY_URL_SESSIONS, headers=headers)
        obj = httpclient.get_json_from_url(requestobj)

        try:
            playing_client = next( c for c in obj if c['Client'] == settings.EmbyConfig.EMBY_PLAYING_CLIENT )
            if 'NowPlayingItem' in playing_client:
                nowplaying_item = playing_client['NowPlayingItem']
                trackname = nowplaying_item['Name']
                artist = "& ".join(nowplaying_item['Artists'])
                album = nowplaying_item['Album']
                return UnifiedData( trackname=trackname,
                                    artist=artist,
                                    album=album,
                                    label=None,
                                    image_url=None,
                                    nowplaying=True)
            else:
                return UnifiedData( trackname=None,
                                    artist=None,
                                    album=None,
                                    label=None,
                                    image_url=None,
                                    nowplaying=False)
        except (KeyError, IndexError) as err:
            _LOGGER.error('Emby search failed to get meaningful results: {err}'.format(
                err=err))
        return None