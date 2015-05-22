import queue
import itertools


class PageIterator:
    def __init__(self, source):
        self.source = source
        self.queue = queue.deque()
        self.is_source_empty = False

    def reset(self):
        self.source.reset()
        self.queue = queue.deque()
        self.is_source_empty = False

    def __next__(self):
        self.prefetch(1)
        try:
            return self.queue.pop()
        except IndexError:
            raise StopIteration()

    def __iter__(self):
        return self

    def fetch(self):
        try:
            next_page = next(self.source)
            for item in next_page:
                self.queue.appendleft(item)
        except StopIteration:
            self.is_source_empty = True

    def prefetch(self, buffer_to):
        if self.buffered_size < buffer_to and not self.is_source_empty:
            self.fetch()
            self.prefetch(buffer_to)

    @property
    def page_size(self):
        return 50

    @property
    def buffered_size(self):
        return len(self.queue)

    def take(self, size=None):
        if size is None:
            size = self.page_size
        return list(itertools.islice(self, size))


def loop_iterator(seq):
    while True:
        for elem in seq:
            yield elem

