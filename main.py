import asyncio
import logging
import logging.handlers
import signal
import sys
import time

from discogs import Discogs
from display import DisplayController
from emby import Emby
from httpclient import HttpClient
from lastfm import LastFm
import settings



_LOGGER = logging.getLogger(__name__)



def setup_logging():
    log_level = settings.GlobalConfig.LOG_LEVEL
    #fmt = "%(asctime)s %(levelname)7s - %(message)s"
    fmt = "%(levelname)7s - %(message)s"
    logging.basicConfig(
        format=fmt,
        level=log_level,
        handlers=[
            logging.handlers.SysLogHandler(address='/dev/log')
        ])

async def main(loop):
    setup_logging()

    display = DisplayController(loop)
    httpclient = HttpClient()

    for signame in ('SIGINT', 'SIGTERM', 'SIGQUIT'):
        loop.add_signal_handler(getattr(signal, signame), lambda: asyncio.ensure_future(cleanup(loop, display, httpclient)))

    data_modules = {
        'parsers': {
            'emby': Emby(),
            'lastfm': LastFm()
        },
        'enrichers': {
            'discogs': Discogs()
        }
    }

    while True:
        if time.time() - display.idle_last_update > settings.GlobalConfig.IDLE_REDRAW_INTERVAL:
            await display.redraw_idle()
        for parser in [ p for _, p in data_modules['parsers'].items() if p.enabled ]:
            if time.time() - parser.last_update > parser.polling_interval:
                data = await parser.refresh()
                if parser.enrichment_required:
                    for enricher in [ e for _, e in data_modules['enrichers'].items() if e.enabled ]:
                        await enricher.enrich(data)
                await display.redraw_detail(httpclient, data)
        display.update(data)
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