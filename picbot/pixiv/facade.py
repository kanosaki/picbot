
from .connection import set_client_credentials
from .api import API

class Pixiv(API):
    def __init__(self, **kwargs):
        if 'client_id' in kwargs and 'client_secret' in kwargs:
            set_client_credentials(kwargs['client_id'], kwargs['client_secret'])
        super().__init__(kwargs['username'], kwargs['password'])


