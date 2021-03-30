from aiohttp import ClientError, ClientSession
import json
import logging
import urllib.request
from urllib.error import HTTPError, URLError



_LOGGER = logging.getLogger(__name__)



def get_json_from_url(request_obj):
    url = request_obj
    headers=()
    data = None
    if isinstance(request_obj, urllib.request.Request):
        url = request_obj.full_url
        headers = request_obj.header_items()
        data = request_obj.data
    _LOGGER.debug('Calling URL [{url}] with headers [{headers}]'.format(
        url=url,
        headers=headers))
    result = "{}"
    try:
        if data:
            data = bytes(json.dumps(data), encoding="utf-8")
        result = urllib.request.urlopen(request_obj, data=data).read().decode()
    except (HTTPError, URLError, ConnectionResetError) as err:
        _LOGGER.error('Got error for URL [{url}] :[{err}]'.format(
            url=url,
            err=err))

    return json.loads(result)

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