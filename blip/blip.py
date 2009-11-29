from oauth import oauth
import urllib
import httplib
import datetime
try:
    import json
except ImportError:
    import simplejson as json
import logging

log = logging.getLogger("blip")

from multipart import encode_multipart_formdata

class BlipError(Exception):
    def __init__(self, status=None, read=None, time=None):
        self.status = status
        self.read = read
        self.time = time or datetime.datetime.now()

    def __repr__(self):
        return "BlipError(%r, %r, %r)" % (self.status, self.read, self.time)

    def __str__(self):
        return repr(self)

class Blip(object):
    protocol = "http://"
    host = 'api.blip.pl'
    port = '80'
    request_token_url = 'http://blip.pl/oauth/request_token'
    access_token_url  = 'http://blip.pl/oauth/access_token'
    authorization_url = 'http://blip.pl/oauth/authorize'
    signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def __init__(self, key=None, secret=None, callback=None):
        self.consumer = oauth.OAuthConsumer(key, secret)
        self.callback = callback
        self.http = httplib.HTTPConnection(self.host, self.port)

    def _request(self, url, method='GET', headers={}, data=None, timeout=None):
        """Make a http request to `url`, with `headers`. If data is
        not None, make it a POST request. Returns a file-like object.

        """
        headers = dict(headers)
        headers['User-Agent'] = 'blipetycje'
        if data:
            data, content_type = encode_multipart_formdata(data)
            headers["Content-type"] = content_type

        log.debug(repr((method, url, data, headers),))

        self.http.request(method, url, data, headers)
        return self.http.getresponse()

    def get_request_token(self):
        oa_req = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            parameters={'oauth_callback': self.callback},
            http_url=self.request_token_url)
        oa_req.sign_request(self.signature_method,
                                  self.consumer,
                                  None)
        req = self._request(self.request_token_url, headers=oa_req.to_header())

        return oauth.OAuthToken.from_string(req.read())

    def get_authorization_url(self):
        """Return the authorization url and token."""
        token = self.get_request_token()
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            token=token,
            parameters={'oauth_callback': self.callback},
            http_url=self.authorization_url,
        )
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        return oauth_request.to_url(), token

    def authorize(self, token, verifier):
        oa_req = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            token=token,
            parameters=dict(oauth_verifier=verifier),
            http_url=self.access_token_url
        )

        oa_req.sign_request(
            self.signature_method,
            self.consumer,
            token
        )
        req = self._request(oa_req.to_url())
        res = req.read()
        return oauth.OAuthToken.from_string(res)

    def prepare_oauth_request(self, url, token, method='GET', **args):
        oa_req = (oauth.OAuthRequest
                  .from_consumer_and_token(self.consumer,
                                           http_url=url,
                                           http_method=method,
                                           parameters=args,
                                           token=token))
        oa_req.sign_request(self.signature_method,
                            self.consumer,
                            token)
        return oa_req

    def get(self, url, *args, **kwargs):
        return self.request(url, 'GET', *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.request(url, method='POST', *args, **kwargs)

    def request(self, url, method='GET', token=None, post_data=None, raw=False, **kwargs):
        headers = ({'Accept': 'application/json', 
                    'X-Blip-api': '0.02'})
        if not url.startswith('http://'):
            url = self.protocol + self.host + url
        if token is not None:
            oa = self.prepare_oauth_request(url, token, method=method, **kwargs)
            headers.update(oa.to_header())
        if kwargs:
            url = "%s?%s" % (url, urllib.urlencode(kwargs))

        res = self._request(url,
                            method=method,
                            data=post_data, 
                            headers=headers)
        if not raw and not str(res.status).startswith('2'):
            raise BlipError(res.status, res.read())
        return json.load(res) if not raw else res
