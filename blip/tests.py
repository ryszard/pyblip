from unittest import TestCase
import os

KEY, SECRET, CALLBACK, TOKEN = [os.environ[l] 
                                for l in 'KEY', 'SECRET', 'CALLBACK', 'TOKEN']
print "Using key: %r, secret: %r, callback: %r" % (KEY, SECRET, CALLBACK)

from blip import Blip
from oauth import oauth

class TestAuth(TestCase):
    def setUp(self):
        self.blip = Blip(key=KEY, secret=SECRET, callback=CALLBACK)

    def test_get_request_token(self):
        token = self.blip.get_request_token()
        self.assert_(isinstance(token, oauth.OAuthToken))
        self.failIf(token.key in ("", None))
        self.failIf(token.secret in ("", None))

    def test_authorization(self):
        url, token = self.blip.get_authorization_url()
        print url, token
        self.assert_(isinstance(token, oauth.OAuthToken))
        self.assert_(url.startswith('http://'), url)
        raw_input("Go to %s and accept" % url)
        access_token = self.blip.authorize(token)
        self.assert_(access_token)
        print access_token

if __name__ == '__main__':
    import unittest
    unittest.main()
