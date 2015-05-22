
import os
import json
from datetime import timedelta
import logging
import itertools

import picbot
from picbot.utils import uniq

import picbot.pixiv.connection

logging.basicConfig(level=logging.DEBUG)
here = os.path.dirname(__file__)

CREDENTIALS_FILE = os.path.join(here, "private", "credentials.json")
credentials = json.load(open(CREDENTIALS_FILE))

pixiv = picbot.Pixiv(**credentials['pixiv'])


def pixiv_ranking():
    for i in range(5):
        yield from pixiv.ranking(date=timedelta(days=-i), size=50)

rankings = list(itertools.islice(uniq(pixiv_ranking()), 100))

cache = picbot.CacheFolder('/tmp/picbot')

# prefetch for Dropbox sync optimization
cache.drain(rankings)

default_sink = picbot.FolderSink('~/Dropbox/Documents/picbot/default', cache)
default_sink.clear()
default_sink.drain(rankings)

cache.cleanup(timedelta(days=-5))
