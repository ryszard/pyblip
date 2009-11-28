from oauth import oauth
import urllib2


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

    def _request(self, url, headers={}, data=None, timeout=None):
        headers = dict(headers)
        request = urllib2.Request(url, data, headers)
        return urllib2.urlopen(request)

    def get_request_token(self):
        oa_req = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
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


    def authorize(self, token):
        oa_req = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer,
            token=token,
            http_url=self.access_token_url
        )

        oa_req.sign_request(
            self.signature_method,
            self.consumer,
            token
        )
        req = self._request(oa_req.to_url())
        res = req.read()
        print res
        return id, oauth.OAuthToken.from_string(res)
