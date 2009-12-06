A light client for the Polish Twitter clone [Blip](http://blip.pl)
that uses OAuth.

Dependencies 
------------

  * [oauth](http://oauth.googlecode.com/svn/code/python/oauth/) from
    SVN, release 1144 and newer.

  * [simplejson](http://pypi.python.org/pypi/simplejson/) if you are
    using Python 2.5.

Features
--------

  * Uses OAuth for authentication.

  * Simple and easy to understand (less than 400 lines of code).

  * It has unit tests.

  * Refuses the temptation to guess the "best" mapping from the
    structure of the REST API to Python methods or from JSON responses
    to Python objects. You are supposed to pass paths as
    arguments. This means that you need to have constantly open only
    *one* document: the [documentation of the
    API](http://www.blip.pl/api-0.02.html), instead of the docs of the
    API *and* `pyblip`. As a bonus, the library shouldn't get out of
    date so quickly.

  * It's easy to make it use a different http client (just write your
    own `Blip._request` and `Blip.initialize_http` methods).

  * If you find the API too verbose for your taste, nothing is
    stopping you from subclassing `blip.Blip` and writing your own
    shortcut methods.

Example
-------

    >>> blip = Blip(key=..., secret=..., callback=...)

    >>> blip.get('/users/szopa')
    {u'avatar_path': u'/users/szopa/avatar', u'background_path': u'/users/szopa/background', u'current_status_path': u'/s/24761884', u'sex': u'm', u'location': u'Warszawa, Polska', u'login': u'szopa', u'id': 29155}

    >>> token=... # this must be an authorized access token

    >>> blip.post('/updates', token=token, post_data={'update[body]': u"Piszę właśnie dokumentację dla #pyblip.a"})
    {u'body': u'Pisz\xc4\x99 w\xc5\x82a\xc5\x9bnie dokumentacj\xc4\x99 dla #pyblip.a', u'user_path': u'/users/szopa', u'created_at': u'2009-12-06 23:37:50', u'type': u'Status', u'id': 24774470, u'transport': {u'name': u'api', u'id': 7}}

    >>> blip.get('/statuses/24774470')
    {u'body': u'Pisz\xc4\x99 w\xc5\x82a\xc5\x9bnie dokumentacj\xc4\x99 dla #pyblip.a', u'user_path': u'/users/szopa', u'created_at': u'2009-12-06 23:37:50', u'type': u'Status', u'id': 24774470, u'transport': {u'name': u'api', u'id': 7}}

Running the tests
-----------------

You will need to pass some information through environent variables:

    $ KEY=yourapikey SECRET=yoursecret CALLBACK=yourcallback USERNAME=yourtestuser TOKEN=anauthorizedtoken python blip/tests.py

You will have to register a Blip app to get KEY, SECRET and
CALLBACK. USERNAME must be a real blip user, and token must be an
authorized access token.

Django example
--------------

It is unfortunate that OAuth is a rather complex technology, so
it is going to be very hard to use it unless you actually understand
what's going on. The [OAuth specification](http://oauth.net/core/1.0a)
is really well written, so it may be a good idea to at least scheme
through it.

For those who like to cut corners, here are some example django views
you could use in order to get an authorized access token (just to get
you started).

    from django.http import HttpResponseRedirect
    from blip import Blip

    blip = Blip(key=..., secret=..., callback=...)

    def auth(request):
        auth_url, token = blip.get_authorization_url()
        request.session['unauthed_token'] = token
        return HttpResponseRedirect(auth_url)

    def return_(request):
        token = request.session['unauthed_token']
        verifier = request.GET['oauth_verifier']
        access_token = blip.authorize(token, verifier)
        ... # do something with the access token


License
-------

See LICENSE.
