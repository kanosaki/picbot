from collections import deque
import json
from datetime import timedelta, datetime
import itertools

import requests

from .connection import AuthConnection
from .utils import format_date
from picbot.pixiv import models


class API(object):
    def __init__(self, username, password, **kwargs):
        self.auth = AuthConnection(username, password)
        self.public = self.auth.public_session

    def ranking(self, **kwargs):
        return Ranking(self)(**kwargs)

    def search(self, query, **kwargs):
        return Search(self)(query, **kwargs)


class APIEndpoint(object):
    base_url = 'https://public-api.secure.pixiv.net/v1/{path}'
    path = None  # set in inherited class

    def __init__(self, api: API):
        self.api = api

    @property
    def connection(self):
        return self.api.auth

    def url(self, path=None):
        p = path or self.path
        return self.base_url.format(path=p)

    def params(self):
        return {
        }

    def __call__(self, *args, **kw):
        raise NotImplementedError()

    def get(self, url=None, params=None):
        url = url or self.url()
        params = params or self.params()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'PixivIOSApp/5.6.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://spapi.pixiv.net/',
            'Accept-Language': 'ja-jp'
        }
        return self.connection.get(url, params=params, headers=headers)

    def parse_body(self, res):
        raise NotImplementedError()


class PagingAPIEndpoint(APIEndpoint):
    def parse_body(self, res: requests.Response):
        try:
            text = res.content.decode('utf-8')
            obj = json.loads(text)
            return obj['response']
        except:  # Format error (originate from http error)
            raise


class Search(PagingAPIEndpoint):
    path = 'search/works'
    modes = {'tag', 'caption'}
    types = {'illustration', 'manga', 'ugoira'}
    orders = {'desc', 'asc'}
    sort = {'date', 'popular'}  # popular is available on paid account only.
    periods = {'all', 'day', 'week', 'month'}

    def validate_args(self, mode, types, order, period):
        if mode not in self.modes:
            raise Exception("%s is not valid mode" % mode)

    def __call__(self, query, mode='caption', types='illustration,manga,ugoira', order='desc', sort='date',
                 period='all'):
        url = self.url()
        params = {
            'q': query,
            'mode': mode,
            'types': types,
            'sort': sort,
            'order': order,
            'period': period,
            'include_stats': 'true',
            'include_sanity_level': 'true',
            'image_sizes': 'small,px_128x128,px_480mw,large',
        }
        return PageIterator(self, url, params)

    def parse_body(self, res: requests.Response):
        resobj = super().parse_body(res)

        def result_mapper(obj):
            return models.create_ranking(obj, self.api)
        return map(result_mapper, resobj)


class Ranking(PagingAPIEndpoint):
    categories = {'all', 'illust', 'manga', 'ugoira', 'novel'}
    modes = {'daily', 'weekly', 'monthly', 'daily_r18', 'weekly_r18', 'monthly_r18'}
    # Only available when category == 'all'
    modes_for_all = {'original', 'rookie', 'male', 'female', 'male_r18', 'female_r18', 'r18g'}

    def validate_args(self, category, mode):
        if category not in self.categories:
            raise Exception("%s is not valid category" % category)
        if mode not in self.modes:
            if category != 'all' or mode not in self.modes_for_all:
                raise Exception("%s is not valid mode" % mode)

    def __call__(self, category='all', mode='daily', date=None, size=None):
        self.validate_args(category, mode)
        path = 'ranking/' + category
        url = self.url(path=path)
        params = {
            'mode': mode,
            'include_stats': 'true',
            'include_sanity_level': 'true',
            # 'profile_image_sizes': 'px_170x170%2Cpx_50x50',
            'image_sizes': 'small,px_128x128,px_480mw,large',
        }
        if date:
            if isinstance(date, timedelta):
                date = datetime.now() + date
            params['date'] = format_date(date)

        it = PageIterator(self, url, params)
        if size:
            return itertools.islice(it, size)
        else:
            return it

    def parse_body(self, res: requests.Response):
        resobj = super().parse_body(res)

        def result_mapper(obj):
            return models.create_ranking(obj, self.api)
        return map(result_mapper, resobj[0]['works'])


class PageIterator(object):
    def __init__(self,
                 api: PagingAPIEndpoint,
                 url: str,
                 params: dict,
                 max_size=None,
                 per_page=50,
                 start_page=1):
        self.per_page = per_page
        self.params = params
        self.page = start_page
        self.max_size = max_size
        self.url = url
        self.buffer = deque()
        self.api = api
        self.consumed_count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.max_size is not None and self.consumed_count > self.max_size:
            raise StopIteration()
        if len(self.buffer) == 0:
            self.buffer_next_page()
        self.consumed_count += 1
        return self.buffer.popleft()

    def buffer_next_page(self):
        next_page = self.page + 1
        for item in self.pull_page(self.page):
            self.buffer.append(item)
        self.page = next_page

    def pull_page(self, next_page):
        params = self.params
        params.update({
            'page': next_page,
            'per_page': self.per_page,
        })
        res = self.api.get(self.url, params=params)
        return self.api.parse_body(res)
