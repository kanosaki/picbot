import time
import json

from requests_oauthlib import OAuth2Session
import requests
from oauthlib.oauth2.rfc6749.clients import Client
from oauthlib.oauth2.rfc6749.parameters import prepare_token_request, OAuth2Token, validate_token_parameters, \
    scope_to_list

AUTH_TOKEN_ENDPOINT = 'https://oauth.secure.pixiv.net/auth/token'

CLIENT_ID = ""
CLIENT_SECRET = ""

def set_client_credentials(client_id, client_secret, **kwargs):
    global CLIENT_ID, CLIENT_SECRET
    CLIENT_ID, CLIENT_SECRET = client_id, client_secret

def parse_token_response(params, scope=None):
    """Refer: oauthlib.oauth2.rfc6749.parameters.parse_token_response"""
    if 'scope' in params:
        params['scope'] = scope_to_list(params['scope'])

    if 'expires' in params:
        params['expires_in'] = params.pop('expires')

    if 'expires_in' in params:
        params['expires_at'] = time.time() + int(params['expires_in'])

    params = OAuth2Token(params, old_scope=scope)
    validate_token_parameters(params)
    return params


class PixivOAuthClient(Client):
    """Refer: oauthlib.oauth2.rfc6749.clients.LegacyApplicationClient

    Pixiv API is basically OAuth2 like protocol.
    But some f**kin' differences are exists.
    This class based on LegacyApplicationClient from oauthlib, but some modifications are applied for Pixiv.
    """

    def __init__(self, client_id, client_secret, **kwargs):
        self.client_secret = client_secret
        super(PixivOAuthClient, self).__init__(client_id, **kwargs)

    def prepare_request_uri(self, *args, **kwargs):
        """This method is not required.... maybe"""
        raise NotImplementedError()

    def prepare_request_body(self, username, password, body='', scope=None, **kwargs):
        """Pixiv requires, client_id, client_secret, username and password."""
        return prepare_token_request('password',
                                     body=body,
                                     username=username,
                                     password=password,
                                     scope=scope,
                                     client_id=self.client_id,
                                     client_secret=self.client_secret,
                                     **kwargs)

    def parse_request_body_response(self, body, scope=None, **kwargs):
        """
        Expects: {"access_token": ...}
        Actual: {"response": {"access_token": ...}, ...}
        """
        param = json.loads(body)
        # Pixiv returns malformed OAuth2 token response.
        if "access_token" not in param and "response" in param:
            param = param["response"]
        self.token = parse_token_response(param, scope=scope)
        self._populate_attributes(self.token)
        return self.token


class AuthConnection(object):
    def __init__(self, username, password, client_id=None, client_secret=None):
        client_id = client_id or CLIENT_ID
        client_secret = client_secret or CLIENT_SECRET
        if not client_id or not client_secret:
            raise Exception("client_id and client_secret required.")
        pixiv_client = PixivOAuthClient(client_id=client_id, client_secret=client_secret)
        self.session = OAuth2Session(client=pixiv_client)
        # Imitate iOS Pixiv App request.
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'PixivIOSApp/5.6.0',
            'Accept': '*/*',
            'Referrer': 'http://www.pixiv.net',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.session.fetch_token(AUTH_TOKEN_ENDPOINT,
                                 headers=headers,
                                 username=username,
                                 password=password)

        # TODO: Check auth result
        self.me = AuthUser(self.session.token['user'])
        self.public_session = requests.session()
        self.public_session.cookies = self.session.cookies
        self.public_session.headers = {
            'Referer': 'http://spapi.pixiv.net/',
            'User-Agent': 'PixivIOSApp/5.6.0',
        }

    def phpsessid(self):
        """Some legacy apis require PHPSESSID as a GET parameter. (not as a cookie)"""
        return self.session.cookies['PHPSESSID']

    def __getattr__(self, key):
        """delegate to session object (get, post, ...)"""
        return getattr(self.session, key)



class AuthUser(object):
    def __init__(self, info_dic: dict):
        self.account = info_dic['account']
        self.id = info_dic['id']
        self.name = info_dic['name']
