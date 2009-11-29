# -*- coding: utf-8 -*-
from unittest import TestCase
import os
import datetime

import logging

log = logging.getLogger("blip")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)
try:
    (KEY, 
     SECRET, 
     CALLBACK, 
     TOKEN) = [os.environ[l] for l in ('KEY', 
                                          'SECRET', 
                                          'CALLBACK', 
                                          'USERNAME', 
                                          'TOKEN')]
except KeyError:
    pass
else:
    print "Using key: %r, secret: %r, callback: %r" % (KEY, SECRET, CALLBACK)

from blip import Blip
from oauth import oauth

class TestAuth(TestCase):
    def setUp(self):
        self.blip = Blip(key=KEY, secret=SECRET, callback=CALLBACK)
        self.token = oauth.OAuthToken.from_string(TOKEN)

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
        print url

    def test_get_with_token(self):
        res = self.blip.request('/users/szopa/updates', 
                                token=self.token, 
                                limit=20, 
                                raw=True)
        self.assertEqual(res.status, 200)
        import json
        json.load(res)

    def test_update(self):
        text = "to jest test {0}".format(datetime.datetime.now())
        res = self.blip.post('/updates',
                             token=self.token,
                             post_data={'update[body]': text},)
                 
        up = self.blip.get('/statuses/%s' % res['id'])
        self.assertEqual(up['id'], res['id'])
        self.assertEqual(up['body'], text)

    def test_unicode(self):
        text = u"to jest test zażółć gęślą jaźń {0}".format(datetime.datetime.now())
        res = self.blip.post('/updates',
                             token=self.token,
                             post_data={'update[body]': text},)
        up = self.blip.get('/statuses/%s' % res['id'])
        self.assertEqual(up['body'], text)
        

                                
    def test_profile(self):
        profile = self.blip.get('/profile', token=self.token)
        self.assert_('id' in profile)

    def test_avatar(self):
        profile = self.blip.get('/users/blipowicztestowicz', token=self.token, include='avatar')
        self.fail(profile)
                                


if __name__ == '__main__':
    import unittest
    unittest.main()
