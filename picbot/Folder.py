import os.path
from datetime import datetime, timedelta
import json


class CacheFolder(object):
    def __init__(self, path):
        self.path = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def cache_path_for(self, item):
        return os.path.join(self.path, item.cache_id)

    def __contains__(self, item):
        return os.path.exists(self.cache_path_for(item))

    def store(self, item, data):
        with open(self.cache_path_for(item), 'wb') as f:
            f.write(data)

    def get(self, item):
        if item in self:
            return open(self.cache_path_for(item), 'rb').read()

    def drain(self, it):
        for item in it:
            if item not in self:
                self.store(item, item.get_image())

    def cleanup(self, remove_thresh):
        files = [os.path.join(self.path, name)
                 for name in os.listdir(self.path)]
        for f in files:
            if not os.path.isfile(f):
                continue
            mtime = datetime.fromtimestamp(os.path.getmtime(f))
            if isinstance(remove_thresh, timedelta):
                remove_thresh = datetime.now() + remove_thresh
            if mtime < remove_thresh:
                os.unlink(f)


class FolderSink(object):
    def __init__(self, path, cache=None,
                 safe=True, metadata_file="metadata.json"):
        self.path = os.path.expanduser(os.path.expandvars(path))
        self.cache = cache or VoidCache()
        self.safe_name = safe
        self.metadata_file = metadata_file
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def drain(self, it):
        files_data = {}
        for item in it:
            image = self.cache.get(item)
            if not image:
                image = item.get_image()
                self.cache.store(item, image)
            if self.safe_name:
                fname = item.safe_filename
            else:
                fname = item.filename
            path = os.path.join(self.path, fname)
            files_data[fname] = item.metadata()
            open(path, 'wb').write(image)
        if self.metadata_file:
            metadata_path = os.path.join(self.path, self.metadata_file)
            json.dump(files_data,
                      open(metadata_path, 'w'),
                      indent=2,
                      sort_keys=True)

    def clear(self):
        directory = self.path
        if not os.path.isdir(directory):
            raise RuntimeError(directory + 'is not valid directory path')
        for file_name in os.listdir(directory):
            path = os.path.join(directory, file_name)
            if os.path.isfile(path):
                os.unlink(path)


class VoidCache(object):
    def __contains__(self, item):
        return False

    def store(self, item, data):
        pass

    def get(self, item):
        pass
