import os.path
import urllib.parse
from picbot.utils import AttrAccess
from picbot.utils.platform import normalize_filename


def create(obj, api):
    if obj['page_count'] > 1:
        return Manga(api, obj)
    else:
        if obj['type'] == 'ugoira':
            return Ugoira(api, obj)
        else:
            return Illust(api, obj)


def create_ranking(obj, api):
    work = obj['work']
    work['rank'] = obj['rank']
    work['previous_rank'] = obj['previous_rank']
    return create(work, api)


class User(AttrAccess):
    pass


class Illust(AttrAccess):
    def __init__(self, api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.user = User(self['user'])

    @property
    def large_image_url(self):
        return self.image_urls.large

    @property
    def extension(self):
        parsed = urllib.parse.urlparse(self.large_image_url)
        path = parsed.path
        _, ext = os.path.splitext(path)
        return ext

    def filename(self):
        name = "{}_{}{}".format(str(self.id), self.title, self.extension)
        return normalize_filename(name)

    def save_to_dir(self, dirpath, api=None):
        api = api or self.api
        save_path = os.path.join(dirpath, self.filename())
        self.save_to(save_path, api)

    def save_to(self, path, api=None):
        api = api or self.api
        large_image = self.image_urls.large
        res = api.public.get(large_image)
        with open(path, 'wb') as f:
            f.write(res.content)

    def __eq__(self, other):
        if hasattr(other, 'id'):
            return self.id == other.id
        else:
            return False

    def __hash__(self):
        return hash(self.id)


class Manga(Illust):
    pass


class Ugoira(Illust):
    pass
