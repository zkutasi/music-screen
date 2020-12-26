import logging



class GlobalConfig(object):
	LOG_LEVEL = logging.DEBUG
	SCREEN_W = 1024
	SCREEN_H = 600
	THUMB_W = 500
	THUMB_H = 500

class DiscogsConfig(object):
	DISCOGS_CONSUMER_KEY = 'cPxFEPpkMBOZpNzmEAob'
	DISCOGS_CONSUMER_SECRET = 'zYBfBGbBYJMmxuaESNLyMLKlBflRlLdq'

class LastFmConfig(object):
	LASTFM_USER = 'zkutasi'
	LASTFM_APIKEY = 'e5a6214a47d5ca04790a7109d1079f51'
	LASTFM_POLLING_INTERVAL = 10