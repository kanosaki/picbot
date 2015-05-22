
def uniq(iter):
    """Make unique iterator with preserving orders. """
    return UniqueIterator(iter)

class UniqueIterator(object):
    def __init__(self, source):
        self.source = source
        self._history = set()

    def __next__(self):
        next_candidate = next(self.source)
        while next_candidate in self._history:
            next_candidate = next(self.source)
        self._history.add(next_candidate)
        return next_candidate


class AttrAccess(dict):
    def __getattr__(self, key):
        try:
            v = self[key]
            if isinstance(v, dict):
                return AttrAccess(**v)
            else:
                return v
        except KeyError:
            raise AttributeError(key)

