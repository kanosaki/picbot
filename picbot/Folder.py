import os.path

class FolderSink(object):
    def __init__(self, path):
        self.path = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def drain(self, it):
        for item in it:
            item.save_to_dir(self.path)

    def clear(self):
        directory = self.path
        if not os.path.isdir(directory):
            raise RuntimeError(directory + 'is not valid directory path')
        for file_name in os.listdir(directory):
            path = os.path.join(directory, file_name)
            if os.path.isfile(path):
                os.unlink(path)


