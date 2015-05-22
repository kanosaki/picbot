
from .connection import set_client_credentials
from .api import API


def Pixiv(**kwargs):
    if 'client_id' in kwargs and 'client_secret' in kwargs:
        set_client_credentials(kwargs['client_id'], kwargs['client_secret'])
    return API(kwargs['username'], kwargs['password'])

