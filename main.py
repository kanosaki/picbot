
import os
import json
from datetime import timedelta
import logging
import itertools

import picbot
from picbot.utils import uniq

import picbot.pixiv.connection

logging.basicConfig(level=logging.WARN)
here = os.path.dirname(__file__)

CREDENTIALS_FILE = os.path.join(here, "private", "credentials.json")
credentials = json.load(open(CREDENTIALS_FILE))

pixiv = picbot.Pixiv(**credentials['pixiv'])


def pixiv_ranking():
    for i in range(10):
        yield from pixiv.ranking(date=timedelta(days=-i), size=50)

def is_squarely(item):
    ratio = float(item.width) / float(item.height)
    return 0.5 < ratio < 2.0

def filter_entry(item):
    return item.page_count == 1 and item.type == 'illustration' and is_squarely(item)

rankings = list(itertools.islice(
    uniq(
        filter(filter_entry,
               pixiv_ranking())),
    100))

cache = picbot.CacheFolder('/tmp/picbot')

# prefetch for Dropbox sync optimization
cache.drain(rankings)

default_sink = picbot.FolderSink('~/Dropbox/Documents/picbot/default', cache, safe=True)
default_sink.clear()
default_sink.drain(rankings)

cache.cleanup(timedelta(days=-10))
