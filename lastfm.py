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
    def __init__(self, trackname, artist, album, image_url, nowplaying):
        self.trackname = trackname
        self.artist = artist
        self.album = album
        self.image_url = image_url
        self.image_present = True
        self.nowplaying = nowplaying
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

    def _get_nowplaying(self, most_recent_track):
        nowplaying = True
        try:
            attr = most_recent_track['@attr']['nowplaying']
            nowplaying = True if attr == 'true' else False
        except (KeyError, IndexError) as err:
            nowplaying = False
        return nowplaying

    def _lastplayed(self):
        url = LASTFM_RECENT_TRACKS_API_URL
        _LOGGER.debug('Refreshing from LastFM URL [{url}]'.format(
            url=url))
        obj = httpclient.get_json_from_url(url)

        try:
            most_recent_track = obj['recenttracks']['track'][0]
            #_LOGGER.debug('Most Recent track JSON: {json}'.format(json=most_recent_track))
            trackname = most_recent_track['name']
            artist = most_recent_track['artist']['#text']
            album = most_recent_track['album']['#text']
            image_url = most_recent_track['image'][3]['#text']
            nowplaying = self._get_nowplaying(most_recent_track)
            return LastFmData(trackname, artist, album, image_url, nowplaying)
        except (KeyError, IndexError) as err:
            _LOGGER.error('LastFM search failed to get meaningful results for URL [{url}]: {err}'.format(
                url=url,
                err=err))
        return None

