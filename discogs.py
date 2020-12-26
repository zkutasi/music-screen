from aiohttp import ClientError, ClientSession
import json
import logging
import re
import time
import urllib.request



DISCOGS_CONSUMER_KEY = 'cPxFEPpkMBOZpNzmEAob'
DISCOGS_CONSUMER_SECRET = 'zYBfBGbBYJMmxuaESNLyMLKlBflRlLdq'
DISCOGS_HEADERS = {
    "Authorization": "Discogs key={key},secret={secret}".format(
        key=DISCOGS_CONSUMER_KEY,
        secret=DISCOGS_CONSUMER_SECRET)
}
DISCOGS_ROOT_URL = 'https://api.discogs.com'
DISCOGS_OMITTED_STRINGS = [
    'EP'
]
_LOGGER = logging.getLogger(__name__)



class DiscogsData(object):
    def __init__(self, image_url, label):
        self.image_url = image_url
        self.label = label


class Discogs(object):
    def __init__(self):
        self.last_update = time.time()

    async def refresh(self, lastfm_data):
        self.last_update = time.time()
        master_url = self._search(lastfm_data.trackname,
            lastfm_data.artist,
            lastfm_data.album)
        self.data = self._get_data_from_resource(master_url)

    def _search(self, trackname, artist, album):
        queryparts = ' '.join([trackname, artist, album]).split()
        queryparts = [ p for p in queryparts if p not in DISCOGS_OMITTED_STRINGS ]
        query = '+'.join(queryparts)
        url = '{root}/database/search?q={query}'.format(
            root=DISCOGS_ROOT_URL,
            query=query)

        requestobj = urllib.request.Request(url, headers=DISCOGS_HEADERS)

        _LOGGER.debug('Calling URL [{url}] with Headers {headers}'.format(
            url=url,
            headers=DISCOGS_HEADERS))
        data = urllib.request.urlopen(requestobj).read().decode()
        obj = json.loads(data)
        return obj['results'][0]['resource_url']

    def _get_data_from_resource(self, url):
        requestobj = urllib.request.Request(url, headers=DISCOGS_HEADERS)

        _LOGGER.debug('Calling URL [{url}] with Headers {headers}'.format(
            url=url,
            headers=DISCOGS_HEADERS))
        data = urllib.request.urlopen(requestobj).read().decode()
        obj = json.loads(data)

        image_url = obj['images'][0]['resource_url']
        label = obj['labels'][0]['name']
        return DiscogsData(image_url, label)
        
