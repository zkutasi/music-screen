import logging
import time

from datamodel import UnifiedData
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



class LastFm(object):
    def __init__(self):
        self.enabled = settings.GlobalConfig.ENABLE_LASTFM
        if self.enabled:
            _LOGGER.debug('Using LastFM URL [{url}]'.format(url=LASTFM_RECENT_TRACKS_API_URL))
            self.polling_interval = settings.LastFmConfig.LASTFM_POLLING_INTERVAL
            self.last_update = 0
            self.data = None
            self.enrichment_required = True

    async def refresh(self):
        self.last_update = time.time()
        data = self._lastplayed()
        self.enrichment_required = (data != self.data)
        self.data = data
        return data

    def _get_nowplaying_audio(self, most_recent_track):
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
            if image_url == LASTFM_EMPTY_IMAGE_URL:
                image_url = None
            nowplaying_audio = self._get_nowplaying_audio(most_recent_track)
            return UnifiedData( trackname=trackname,
                                artist=artist,
                                album=album,
                                label=None,
                                image_url=image_url,
                                nowplaying_type=UnifiedData.AUDIO)
        except (KeyError, IndexError) as err:
            _LOGGER.error('LastFM search failed to get meaningful results for URL [{url}]: {err}'.format(
                url=url,
                err=err))
        return None

