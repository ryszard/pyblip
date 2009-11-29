# -*- coding: utf-8 -*-
from unittest import TestCase
import os
import datetime

import logging

log = logging.getLogger("blip")
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
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

from blip import Blip, BlipError
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
        try:
            import json
        except ImportError:
            import simplejson as json
        json.load(res)

    def test_update(self):
        text = "to jest test %s" % datetime.datetime.now()
        res = self.blip.post('/updates',
                             token=self.token,
                             post_data={'update[body]': text},)
                 
        up = self.blip.get('/statuses/%s' % res['id'])
        self.assertEqual(up['id'], res['id'])
        self.assertEqual(up['body'], text)

    def test_update_too_long(self):
        text = ("to jest test %s" % (datetime.datetime.now())) * 20
        self.assertRaises(BlipError, 
                          self.blip.post,
                          '/updates',
                          token=self.token,
                          post_data={'update[body]': text},)
    def test_unicode(self):
        text = u"to jest test zażółć gęślą jaźń %s" % (datetime.datetime.now())
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
        self.assert_('avatar' in profile)

    def test_shorturl(self):
        link = 'http://gryziemy.net/2009/6/29/czego-brakuje-flakerowi-i-blipowi'
        res = self.blip.post('/shortlinks',
                             token=self.token,
                             post_data={'shortlink[original_link]': link})
        self.assert_('url' in res, res)
                                


if __name__ == '__main__':
    import unittest
    unittest.main()
