import json
import logging
import time
import urllib.request



LASTFM_ROOT_URL = 'http://ws.audioscrobbler.com/2.0'
LASTFM_USER = 'zkutasi'
LASTFM_APIKEY = 'e5a6214a47d5ca04790a7109d1079f51'
LASTFM_RECENT_TRACKS_API_URL = '{root}/?method=user.getrecenttracks&user={user}&api_key={apikey}&limit={limit}&format=json'.format(
    root=LASTFM_ROOT_URL,
    user=LASTFM_USER,
    apikey=LASTFM_APIKEY,
    limit=2)
LASTFM_EMPTY_IMAGE_URL = 'https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png'
_LOGGER = logging.getLogger(__name__)



class LastFmData(object):
    def __init__(self, trackname, artist, album, image_url):
        self.trackname = trackname
        self.artist = artist
        self.album = album
        self.image_url = image_url
        self.image_present = True
        if image_url == LASTFM_EMPTY_IMAGE_URL:
            self.image_present = False

    def __eq__(self, other):
        if isinstance(other, LastFmData):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return str(self.__dict__)



class LastFm(object):
    def __init__(self):
        _LOGGER.debug('Using LastFM URL [{url}]'.format(url=LASTFM_RECENT_TRACKS_API_URL))
        self.last_update = time.time() - 100
        self.data = None
        self.update_required = True

    async def refresh(self):
        self.last_update = time.time()
        data = self._lastplayed()
        self.update_required = (data != self.data)
        self.data = data

    def _lastplayed(self):
        _LOGGER.debug('Refreshing from LastFM URL [{url}]'.format(
            url=LASTFM_RECENT_TRACKS_API_URL))
        data = urllib.request.urlopen(LASTFM_RECENT_TRACKS_API_URL).read().decode()
        obj = json.loads(data)

        trackname = obj['recenttracks']['track'][0]['name']
        artist = obj['recenttracks']['track'][0]['artist']['#text']
        album = obj['recenttracks']['track'][0]['album']['#text']
        image_url = obj['recenttracks']['track'][0]['image'][3]['#text']

        return LastFmData(trackname, artist, album, image_url)

