from aiohttp import ClientError, ClientSession
import json
import logging
import urllib.request
from urllib.error import HTTPError, URLError



_LOGGER = logging.getLogger(__name__)



def get_json_from_url(url):
    if isinstance(url, urllib.request.Request):
        _LOGGER.debug('Calling URL [{url}]'.format(url=url.full_url))
    else:
        _LOGGER.debug('Calling URL [{url}]'.format(url=url))
    data = '{}'
    try:
        data = urllib.request.urlopen(url).read().decode()
    except HTTPError as err:
        _LOGGER.error('Got HTTP error for URL [{url}] :[{err}]'.format(
            url=url,
            err=err))
    except URLError as err:
        _LOGGER.error('Got error for URL [{url}] :[{err}]'.format(
            url=url,
            err=err))

    return json.loads(data)

class HttpClient(object):
    def __init__(self):
        self.session = ClientSession()

    async def cleanup(self):
        await self.session.close()

    async def get_image_data(self, url):
        if not url:
            return None

        try:
            _LOGGER.debug('Downloading image [{url}]'.format(url=url))
            async with self.session.get(url) as response:
                content_type = response.headers.get('content-type')
                if content_type and not content_type.startswith('image/'):
                    _LOGGER.warning("Not a valid image type [{type}] from URL [{url}]".format(
                        type=content_type,
                        url=url))
                    return None
                return await response.read()
        except ClientError as err:
            _LOGGER.warning("Problem connecting to URL [{url}]: [{err}]".format(
                url=url,
                err=err))
        except Exception as err:
            _LOGGER.warning("Image failed to load from URL [{url}]: [{err}]".format(
                url=url,
                err=err))
        return None