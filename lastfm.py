import logging
import time

import httpclient
import settings



LASTFM_ROOT_URL = 'http://ws.audioscrobbler.com/2.0'
LASTFM_USER = settings.LastFmConfig.LASTFM_USER
LASTFM_APIKEY = settings.LastFmConfig.LASTFM_APIKEY
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
        self.last_update = time.time() - 10*settings.LastFmConfig.LASTFM_POLLING_INTERVAL
        self.data = None
        self.update_required = True

    async def refresh(self):
        self.last_update = time.time()
        data = self._lastplayed()
        self.update_required = (data != self.data)
        self.data = data

    def _lastplayed(self):
        url = LASTFM_RECENT_TRACKS_API_URL
        _LOGGER.debug('Refreshing from LastFM URL [{url}]'.format(
            url=url))
        obj = httpclient.get_json_from_url(url)

        try:
            trackname = obj['recenttracks']['track'][0]['name']
            artist = obj['recenttracks']['track'][0]['artist']['#text']
            album = obj['recenttracks']['track'][0]['album']['#text']
            image_url = obj['recenttracks']['track'][0]['image'][3]['#text']
            return LastFmData(trackname, artist, album, image_url)
        except (KeyError, IndexError):
            _LOGGER.error('LastFM search failed to get meaningful results for URL [{url}]'.format(
                url=url))
        return None

