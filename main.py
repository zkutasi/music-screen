import asyncio
import logging
import signal
import time

from discogs import Discogs
from display import DisplayController
from httpclient import HttpClient
from lastfm import LastFm
import settings



_LOGGER = logging.getLogger(__name__)



def setup_logging():
    log_level = settings.GlobalConfig.LOG_LEVEL
    fmt = "%(asctime)s %(levelname)7s - %(message)s"
    logging.basicConfig(format=fmt, level=log_level)

async def main(loop):
    setup_logging()

    display = DisplayController(loop)
    httpclient = HttpClient()

    for signame in ('SIGINT', 'SIGTERM', 'SIGQUIT'):
        loop.add_signal_handler(getattr(signal, signame), lambda: asyncio.ensure_future(cleanup(loop, display, httpclient)))

    data = {
    	'lastfm': LastFm(),
    	'discogs': Discogs()
    }

    while True:
        if time.time() - data['lastfm'].last_update > settings.LastFmConfig.LASTFM_POLLING_INTERVAL:
            await data['lastfm'].refresh()
            if data['lastfm'].update_required:
            	await data['discogs'].refresh(data['lastfm'].data)
            	await display.redraw(httpclient, data)
        await asyncio.sleep(1)

async def cleanup(loop, display, httpclient):
    _LOGGER.debug("Shutting down")
    display.cleanup()
    await httpclient.cleanup()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main(loop))
        loop.run_forever()
    finally:
        loop.close()