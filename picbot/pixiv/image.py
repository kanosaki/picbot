import os.path
import urllib.parse
from picbot.utils import AttrAccess
from picbot.utils.platform import normalize_filename

def create(obj):
    if obj['page_count'] > 1:
        return Manga(obj)
    else:
        if obj['type'] == 'ugoira':
            return Ugoira(obj)
        else:
            return Illust(obj)

def create_ranking(obj):
    work = obj['work']
    work['rank'] = obj['rank']
    work['previous_rank'] = obj['previous_rank']
    return create(work)

class Illust(AttrAccess):
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

    def save_to_dir(self, dirpath, api):
        save_path = os.path.join(dirpath, self.filename())
        self.save_to(save_path, api)

    def save_to(self, path, api):
        large_image = self.image_urls.large
        res = api.public.get(large_image)
        with open(path, 'wb') as f:
            f.write(res.content)

class Manga(Illust):
    pass


class Ugoira(Illust):
    pass


