from aiohttp import ClientError, ClientSession
import json
import logging
import re
import time
import urllib.parse

import httpclient
import settings



DISCOGS_CONSUMER_KEY = settings.DiscogsConfig.DISCOGS_CONSUMER_KEY
DISCOGS_CONSUMER_SECRET = settings.DiscogsConfig.DISCOGS_CONSUMER_SECRET
DISCOGS_HEADERS = {
    "Authorization": "Discogs key={key},secret={secret}".format(
        key=DISCOGS_CONSUMER_KEY,
        secret=DISCOGS_CONSUMER_SECRET)
}
DISCOGS_ROOT_URL = 'https://api.discogs.com'
DISCOGS_OMITTED_WORDS = [
    'EP', '-'
]
_LOGGER = logging.getLogger(__name__)



class DiscogsData(object):
    def __init__(self, image_url, label):
        self.image_url = image_url
        self.label = label


class Discogs(object):
    def __init__(self):
        self.last_update = time.time()
        self.data = None

    async def refresh(self, lastfm_data):
        self.last_update = time.time()
        if not lastfm_data:
            return 
        resource_url = self._search(lastfm_data.trackname,
            lastfm_data.artist,
            lastfm_data.album)
        if resource_url:
            self.data = self._get_data_from_resource(resource_url)

    def _search(self, trackname, artist, album):
        queryparts = ' '.join([trackname, artist, album]).split()
        queryparts = [ p for p in queryparts if p not in DISCOGS_OMITTED_WORDS ]
        query = ' '.join(queryparts)
        query = urllib.parse.quote_plus(query)
        url = '{root}/database/search?q={query}'.format(
            root=DISCOGS_ROOT_URL,
            query=query)

        requestobj = urllib.request.Request(url, headers=DISCOGS_HEADERS)

        _LOGGER.debug('Calling discogs URL [{url}] with Headers {headers}'.format(
            url=url,
            headers=DISCOGS_HEADERS))
        obj = httpclient.get_json_from_url(requestobj)
        try:
            return obj['results'][0]['resource_url']
        except (KeyError, IndexError) as err:
            _LOGGER.error('Discogs search failed to get meaningful results for URL [{url}]: {err}'.format(
                url=url,
                err=err))
        return None

    def _get_data_from_resource(self, url):
        requestobj = urllib.request.Request(url, headers=DISCOGS_HEADERS)

        _LOGGER.debug('Calling discogs URL [{url}] with Headers {headers}'.format(
            url=url,
            headers=DISCOGS_HEADERS))
        obj = httpclient.get_json_from_url(requestobj)
        
        try:
            image_url = obj['images'][0]['resource_url'] if 'images' in obj else None
            label = obj['labels'][0]['name'] if 'labels' in obj else None
            return DiscogsData(image_url, label)
        except (KeyError, IndexError) as err:
            _LOGGER.error('Discogs data fetch failed to get meaningful results for URL [{url}]: {err}'.format(
                url=url,
                err=err))
        return None
