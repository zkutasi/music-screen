from aiohttp import ClientError, ClientSession
import logging



_LOGGER = logging.getLogger(__name__)



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