__FILENAME__ = reltime
from datetime import datetime
import math
def reltime(date, compare_to=None, at='@'):
    r'''Takes a datetime and returns a relative representation of the
    time.
    :param date: The date to render relatively
    :param compare_to: what to compare the date to. Defaults to datetime.now()
    :param at: date/time separator. defaults to "@". "at" is also reasonable.
 
    >>> from datetime import datetime, timedelta
    >>> today = datetime(2050, 9, 2, 15, 00)
    >>> earlier = datetime(2050, 9, 2, 12)
    >>> reltime(earlier, today)
    'today @ 12pm'
    >>> yesterday = today - timedelta(1)
    >>> reltime(yesterday, compare_to=today)
    'yesterday @ 3pm'
    >>> reltime(datetime(2050, 9, 1, 15, 32), today)
    'yesterday @ 3:32pm'
    >>> reltime(datetime(2050, 8, 31, 16), today)
    'Wednesday @ 4pm (2 days ago)'
    >>> reltime(datetime(2050, 8, 26, 14), today)
    'last Friday @ 2pm (7 days ago)'
    >>> reltime(datetime(2049, 9, 2, 12, 00), today)
    'September 2nd, 2049 @ 12pm (last year)'
    >>> today = datetime(2012, 8, 29, 13, 52)
    >>> last_mon = datetime(2012, 8, 20, 15, 40, 55)
    >>> reltime(last_mon, today)
    'last Monday @ 3:40pm (9 days ago)'
    '''
    def ordinal(n):
        r'''Returns a string ordinal representation of a number
        Taken from: http://stackoverflow.com/a/739301/180718
        '''
        if 10 <= n % 100 < 20:
            return str(n) + 'th'
        else:
            return str(n) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, "th")
 
    compare_to = compare_to or datetime.now()
    if date > compare_to:
        return NotImplementedError('reltime only handles dates in the past')
    #get timediff values
    diff = compare_to - date
    if diff.seconds < 60 * 60 * 8: #less than a business day?
        days_ago = diff.days
    else:
        days_ago = diff.days + 1
    months_ago = compare_to.month - date.month
    years_ago = compare_to.year - date.year
    weeks_ago = int(math.ceil(days_ago / 7.0))
    #get a non-zero padded 12-hour hour
    hr = date.strftime('%I')
    if hr.startswith('0'):
        hr = hr[1:]
    wd = compare_to.weekday()
    #calculate the time string
    if date.minute == 0:
        time = '{0}{1}'.format(hr, date.strftime('%p').lower())
    else:
        time = '{0}:{1}'.format(hr, date.strftime('%M%p').lower())
    #calculate the date string
    if days_ago == 0:
        datestr = 'today {at} {time}'
    elif days_ago == 1:
        datestr = 'yesterday {at} {time}'
    elif (wd in (5, 6) and days_ago in (wd+1, wd+2)) or \
            wd + 3 <= days_ago <= wd + 8:
        #this was determined by making a table of wd versus days_ago and
        #divining a relationship based on everyday speech. This is somewhat
        #subjective I guess!
        datestr = 'last {weekday} {at} {time} ({days_ago} days ago)'
    elif days_ago <= wd + 2:
        datestr = '{weekday} {at} {time} ({days_ago} days ago)'
    elif years_ago == 1:
        datestr = '{month} {day}, {year} {at} {time} (last year)'
    elif years_ago > 1:
        datestr = '{month} {day}, {year} {at} {time} ({years_ago} years ago)'
    elif months_ago == 1:
        datestr = '{month} {day} {at} {time} (last month)'
    elif months_ago > 1:
        datestr = '{month} {day} {at} {time} ({months_ago} months ago)'
    else: 
        #not last week, but not last month either
        datestr = '{month} {day} {at} {time} ({days_ago} days ago)'
    return datestr.format(time=time,
                          weekday=date.strftime('%A'),
                          day=ordinal(date.day),
                          days=diff.days,
                          days_ago=days_ago,
                          month=date.strftime('%B'),
                          years_ago=years_ago,
                          months_ago=months_ago,
                          weeks_ago=weeks_ago,
                          year=date.year,
                          at=at)
########NEW FILE########
__FILENAME__ = ansi
"""
Support for ANSI colours in command-line client.

.. data:: ESC
    ansi escape character

.. data:: RESET
    ansi reset colour (ansi value)

.. data:: COLOURS_NAMED
    dict of colour names mapped to their ansi value

.. data:: COLOURS_MIDS
    A list of ansi values for Mid Spectrum Colours
"""

import itertools
import sys

ESC = chr(0x1B)
RESET = "0"

COLOURS_NAMED = dict(list(zip(
    ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'],
    [str(x) for x in range(30, 38)]
)))
COLOURS_MIDS = [
    colour for name, colour in list(COLOURS_NAMED.items())
    if name not in ('black', 'white')
]

class AnsiColourException(Exception):
    ''' Exception while processing ansi colours '''
    pass

class ColourMap(object):
    '''
    Object that allows for mapping strings to ansi colour values.
    '''
    def __init__(self, colors=COLOURS_MIDS):
        ''' uses the list of ansi `colors` values to initialize the map '''
        self._cmap = {}
        self._colourIter = itertools.cycle(colors)

    def colourFor(self, string):
        '''
        Returns an ansi colour value given a `string`.
        The same ansi colour value is always returned for the same string
        '''
        if string not in self._cmap:
            self._cmap[string] = next(self._colourIter)
        return self._cmap[string]

class AnsiCmd(object):
    def __init__(self, forceAnsi):
        self.forceAnsi = forceAnsi

    def cmdReset(self):
        ''' Returns the ansi cmd colour for a RESET '''
        if sys.stdout.isatty() or self.forceAnsi:
            return ESC + "[0m"
        else:
            return ""

    def cmdColour(self, colour):
        '''
        Return the ansi cmd colour (i.e. escape sequence)
        for the ansi `colour` value
        '''
        if sys.stdout.isatty() or self.forceAnsi:
            return ESC + "[" + colour + "m"
        else:
            return ""

    def cmdColourNamed(self, colour):
        ''' Return the ansi cmdColour for a given named `colour` '''
        try:
            return self.cmdColour(COLOURS_NAMED[colour])
        except KeyError:
            raise AnsiColourException('Unknown Colour %s' % (colour))

    def cmdBold(self):
        if sys.stdout.isatty() or self.forceAnsi:
            return ESC + "[1m"
        else:
            return ""

    def cmdUnderline(self):
        if sys.stdout.isatty() or self.forceAnsi:
            return ESC + "[4m"
        else:
            return ""

"""These exist to maintain compatibility with users of version<=1.9.0"""
def cmdReset():
    return AnsiCmd(False).cmdReset()

def cmdColour(colour):
    return AnsiCmd(False).cmdColour(colour)

def cmdColourNamed(colour):
    return AnsiCmd(False).cmdColourNamed(colour)

########NEW FILE########
__FILENAME__ = api
try:
    import urllib.request as urllib_request
    import urllib.error as urllib_error
except ImportError:
    import urllib2 as urllib_request
    import urllib2 as urllib_error

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from .twitter_globals import POST_ACTIONS
from .auth import NoAuth

import re
import gzip

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client

try:
    import json
except ImportError:
    import simplejson as json


class _DEFAULT(object):
    pass

class TwitterError(Exception):
    """
    Base Exception thrown by the Twitter object when there is a
    general error interacting with the API.
    """
    pass

class TwitterHTTPError(TwitterError):
    """
    Exception thrown by the Twitter object when there is an
    HTTP error interacting with twitter.com.
    """
    def __init__(self, e, uri, format, uriparts):
        self.e = e
        self.uri = uri
        self.format = format
        self.uriparts = uriparts
        try:
            data = self.e.fp.read()
        except http_client.IncompleteRead as e:
            # can't read the error text
            # let's try some of it
            data = e.partial
        if self.e.headers.get('Content-Encoding') == 'gzip':
            buf = StringIO(data)
            f = gzip.GzipFile(fileobj=buf)
            self.response_data = f.read()
        else:
            self.response_data = data
        super(TwitterHTTPError, self).__init__(str(self))

    def __str__(self):
        fmt = ("." + self.format) if self.format else ""
        return (
            "Twitter sent status %i for URL: %s%s using parameters: "
            "(%s)\ndetails: %s" %(
                self.e.code, self.uri, fmt, self.uriparts,
                self.response_data))

class TwitterResponse(object):
    """
    Response from a twitter request. Behaves like a list or a string
    (depending on requested format) but it has a few other interesting
    attributes.

    `headers` gives you access to the response headers as an
    httplib.HTTPHeaders instance. You can do
    `response.headers.get('h')` to retrieve a header.
    """
    def __init__(self, headers):
        self.headers = headers

    @property
    def rate_limit_remaining(self):
        """
        Remaining requests in the current rate-limit.
        """
        return int(self.headers.get('X-Rate-Limit-Remaining', "0"))

    @property
    def rate_limit_limit(self):
        """
        The rate limit ceiling for that given request.
        """
        return int(self.headers.get('X-Rate-Limit-Limit', "0"))

    @property
    def rate_limit_reset(self):
        """
        Time in UTC epoch seconds when the rate limit will reset.
        """
        return int(self.headers.get('X-Rate-Limit-Reset', "0"))


def wrap_response(response, headers):
    response_typ = type(response)
    if response_typ is bool:
        # HURF DURF MY NAME IS PYTHON AND I CAN'T SUBCLASS bool.
        response_typ = int
    elif response_typ is str:
        return response

    class WrappedTwitterResponse(response_typ, TwitterResponse):
        __doc__ = TwitterResponse.__doc__

        def __init__(self, response, headers):
            response_typ.__init__(self, response)
            TwitterResponse.__init__(self, headers)
        def __new__(cls, response, headers):
            return response_typ.__new__(cls, response)

    return WrappedTwitterResponse(response, headers)



class TwitterCall(object):

    def __init__(
        self, auth, format, domain, callable_cls, uri="",
        uriparts=None, secure=True, timeout=None, gzip=False):
        self.auth = auth
        self.format = format
        self.domain = domain
        self.callable_cls = callable_cls
        self.uri = uri
        self.uriparts = uriparts
        self.secure = secure
        self.timeout = timeout
        self.gzip = gzip

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            def extend_call(arg):
                return self.callable_cls(
                    auth=self.auth, format=self.format, domain=self.domain,
                    callable_cls=self.callable_cls, timeout=self.timeout,
                    secure=self.secure, gzip=self.gzip,
                    uriparts=self.uriparts + (arg,))
            if k == "_":
                return extend_call
            else:
                return extend_call(k)

    def __call__(self, **kwargs):
        # Build the uri.
        uriparts = []
        for uripart in self.uriparts:
            # If this part matches a keyword argument, use the
            # supplied value otherwise, just use the part.
            uriparts.append(str(kwargs.pop(uripart, uripart)))
        uri = '/'.join(uriparts)

        method = kwargs.pop('_method', None)
        if not method:
            method = "GET"
            for action in POST_ACTIONS:
                if re.search("%s(/\d+)?$" % action, uri):
                    method = "POST"
                    break

        # If an id kwarg is present and there is no id to fill in in
        # the list of uriparts, assume the id goes at the end.
        id = kwargs.pop('id', None)
        if id:
            uri += "/%s" %(id)

        # If an _id kwarg is present, this is treated as id as a CGI
        # param.
        _id = kwargs.pop('_id', None)
        if _id:
            kwargs['id'] = _id

        # If an _timeout is specified in kwargs, use it
        _timeout = kwargs.pop('_timeout', None)

        secure_str = ''
        if self.secure:
            secure_str = 's'
        dot = ""
        if self.format:
            dot = "."
        uriBase = "http%s://%s/%s%s%s" %(
                    secure_str, self.domain, uri, dot, self.format)

        # Catch media arguments to handle oauth query differently for multipart
        media = None
        for arg in ['media[]', 'banner', 'image']:
            if arg in kwargs:
                media = kwargs.pop(arg)
                mediafield = arg
                break

        headers = {'Accept-Encoding': 'gzip'} if self.gzip else dict()
        body = None; arg_data = None
        if self.auth:
            headers.update(self.auth.generate_headers())
            # Use urlencoded oauth args with no params when sending media
            # via multipart and send it directly via uri even for post
            arg_data = self.auth.encode_params(uriBase, method,
                {} if media else kwargs )
            if method == 'GET' or media:
                uriBase += '?' + arg_data
            else:
                body = arg_data.encode('utf8')

        # Handle query as multipart when sending media
        if media:
            BOUNDARY = "###Python-Twitter###"
            bod = []
            bod.append('--' + BOUNDARY)
            bod.append('Content-Disposition: form-data; name="%s"' %
                mediafield)
            bod.append('')
            bod.append(media)
            for k, v in kwargs.items():
                bod.append('--' + BOUNDARY)
                bod.append('Content-Disposition: form-data; name="%s"' % k)
                bod.append('')
                bod.append(v)
            bod.append('--' + BOUNDARY + '--')
            body = '\r\n'.join(bod)
            headers['Content-Type'] = 'multipart/form-data; boundary=%s' % BOUNDARY

        req = urllib_request.Request(uriBase, body, headers)
        return self._handle_response(req, uri, arg_data, _timeout)

    def _handle_response(self, req, uri, arg_data, _timeout=None):
        kwargs = {}
        if _timeout:
            kwargs['timeout'] = _timeout
        try:
            handle = urllib_request.urlopen(req, **kwargs)
            if handle.headers['Content-Type'] in ['image/jpeg', 'image/png']:
                return handle
            try:
                data = handle.read()
            except http_client.IncompleteRead as e:
                # Even if we don't get all the bytes we should have there
                # may be a complete response in e.partial
                data = e.partial
            if handle.info().get('Content-Encoding') == 'gzip':
                # Handle gzip decompression
                buf = StringIO(data)
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            if "json" == self.format:
                res = json.loads(data.decode('utf8'))
                return wrap_response(res, handle.headers)
            else:
                return wrap_response(
                    data.decode('utf8'), handle.headers)
        except urllib_error.HTTPError as e:
            if (e.code == 304):
                return []
            else:
                raise TwitterHTTPError(e, uri, self.format, arg_data)

class Twitter(TwitterCall):
    """
    The minimalist yet fully featured Twitter API class.

    Get RESTful data by accessing members of this class. The result
    is decoded python objects (lists and dicts).

    The Twitter API is documented at:

      http://dev.twitter.com/doc


    Examples::

        t = Twitter(
            auth=OAuth(token, token_key, con_secret, con_secret_key)))

        # Get your "home" timeline
        t.statuses.home_timeline()

        # Get a particular friend's tweets
        t.statuses.user_timeline(user_id="billybob")

        # Update your status
        t.statuses.update(
            status="Using @sixohsix's sweet Python Twitter Tools.")

        # Send a direct message
        t.direct_messages.new(
            user="billybob",
            text="I think yer swell!")

        # Get the members of tamtar's list "Things That Are Rad"
        t._("tamtar")._("things-that-are-rad").members()

        # Note how the magic `_` method can be used to insert data
        # into the middle of a call. You can also use replacement:
        t.user.list.members(user="tamtar", list="things-that-are-rad")

        # An *optional* `_timeout` parameter can also be used for API
        # calls which take much more time than normal or twitter stops
        # responding for some reasone
        t.users.lookup(
            screen_name=','.join(A_LIST_OF_100_SCREEN_NAMES), \
            _timeout=1)



    Searching Twitter::

        # Search for the latest tweets about #pycon
        t.search.tweets(q="#pycon")


    Using the data returned
    -----------------------

    Twitter API calls return decoded JSON. This is converted into
    a bunch of Python lists, dicts, ints, and strings. For example::

        x = twitter.statuses.home_timeline()

        # The first 'tweet' in the timeline
        x[0]

        # The screen name of the user who wrote the first 'tweet'
        x[0]['user']['screen_name']


    Getting raw XML data
    --------------------

    If you prefer to get your Twitter data in XML format, pass
    format="xml" to the Twitter object when you instantiate it::

        twitter = Twitter(format="xml")

    The output will not be parsed in any way. It will be a raw string
    of XML.

    """
    def __init__(
        self, format="json",
        domain="api.twitter.com", secure=True, auth=None,
        api_version=_DEFAULT):
        """
        Create a new twitter API connector.

        Pass an `auth` parameter to use the credentials of a specific
        user. Generally you'll want to pass an `OAuth`
        instance::

            twitter = Twitter(auth=OAuth(
                    token, token_secret, consumer_key, consumer_secret))


        `domain` lets you change the domain you are connecting. By
        default it's `api.twitter.com` but `search.twitter.com` may be
        useful too.

        If `secure` is False you will connect with HTTP instead of
        HTTPS.

        `api_version` is used to set the base uri. By default it's
        '1'. If you are using "search.twitter.com" set this to None.
        """
        if not auth:
            auth = NoAuth()

        if (format not in ("json", "xml", "")):
            raise ValueError("Unknown data format '%s'" %(format))

        if api_version is _DEFAULT:
            api_version = '1.1'

        uriparts = ()
        if api_version:
            uriparts += (str(api_version),)

        TwitterCall.__init__(
            self, auth=auth, format=format, domain=domain,
            callable_cls=TwitterCall,
            secure=secure, uriparts=uriparts)


__all__ = ["Twitter", "TwitterError", "TwitterHTTPError", "TwitterResponse"]

########NEW FILE########
__FILENAME__ = archiver
"""USAGE
    twitter-archiver [options] <-|user> [<user> ...]

DESCRIPTION
    Archive tweets of users, sorted by date from oldest to newest, in
    the following format: <id> <date> <<screen_name>> <tweet_text>
    Date format is: YYYY-MM-DD HH:MM:SS TZ. Tweet <id> is used to
    resume archiving on next run. Archive file name is the user name.
    Provide "-" instead of users to read users from standard input.

OPTIONS
 -o --oauth            authenticate to Twitter using OAuth (default: no)
 -s --save-dir <path>  directory to save archives (default: current dir)
 -a --api-rate         see current API rate limit status
 -t --timeline <file>  archive own timeline into given file name (requires
                       OAuth, max 800 statuses)
 -m --mentions <file>  archive own mentions instead of timeline into
                       given file name (requires OAuth, max 800 statuses)
 -v --favorites        archive user's favorites instead of timeline
 -f --follow-redirects follow redirects of urls
 -r --redirect-sites   follow redirects for this comma separated list of hosts
 -d --dms <file>       archive own direct messages (both received and
                       sent) into given file name.
 -i --isoformat        store dates in ISO format (specifically RFC 3339)

AUTHENTICATION
    Authenticate to Twitter using OAuth to archive tweets of private profiles
    and have higher API rate limits. OAuth authentication tokens are stored
    in ~/.twitter-archiver_oauth.
"""

from __future__ import print_function

import os, sys, time as _time, calendar, functools
from datetime import time, date, datetime
from getopt import gnu_getopt as getopt, GetoptError

try:
    import urllib.request as urllib2
    import http.client as httplib
except ImportError:
    import urllib2
    import httplib


# T-Archiver (Twitter-Archiver) application registered by @stalkr_
CONSUMER_KEY='d8hIyfzs7ievqeeZLjZrqQ'
CONSUMER_SECRET='AnZmK0rnvaX7BoJ75l6XlilnbyMv7FoiDXWVmPD8'

from .api import Twitter, TwitterError
from .oauth import OAuth, read_token_file
from .oauth_dance import oauth_dance
from .auth import NoAuth
from .util import Fail, err, expand_line, parse_host_list
from .follow import lookup
from .timezones import utc as UTC, Local

def parse_args(args, options):
    """Parse arguments from command-line to set options."""
    long_opts = ['help', 'oauth', 'save-dir=', 'api-rate', 'timeline=', 'mentions=', 'favorites', 'follow-redirects',"redirect-sites=", 'dms=', 'isoformat']
    short_opts = "hos:at:m:vfr:d:i"
    opts, extra_args = getopt(args, short_opts, long_opts)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            raise SystemExit(0)
        elif opt in ('-o', '--oauth'):
            options['oauth'] = True
        elif opt in ('-s', '--save-dir'):
            options['save-dir'] = arg
        elif opt in ('-a', '--api-rate'):
            options['api-rate' ] = True
        elif opt in ('-t', '--timeline'):
            options['timeline'] = arg
        elif opt in ('-m', '--mentions'):
            options['mentions'] = arg
        elif opt in ('-v', '--favorites'):
            options['favorites'] = True
        elif opt in ('-f', '--follow-redirects'):
            options['follow-redirects'] = True
        elif opt in ('-r', '--redirect-sites'):
            options['redirect-sites'] = arg
        elif opt in ('-d', '--dms'):
            options['dms'] = arg
        elif opt in ('-i', '--isoformat'):
            options['isoformat'] = True

    options['extra_args'] = extra_args

def load_tweets(filename):
    """Load tweets from file into dict, see save_tweets()."""
    try:
        archive = open(filename,"r")
    except IOError: # no archive (yet)
        return {}

    tweets = {}
    for line in archive.readlines():
        tid, text = line.strip().split(" ", 1)
        tweets[int(tid)] = text.decode("utf-8")

    archive.close()
    return tweets

def save_tweets(filename, tweets):
    """Save tweets from dict to file.

    Save tweets from dict to UTF-8 encoded file, one per line:
        <tweet id (number)> <tweet text>
    Tweet text is:
        <date> <<user>> [RT @<user>: ]<text>

    Args:
        filename: A string representing the file name to save tweets to.
        tweets: A dict mapping tweet-ids (int) to tweet text (str).
    """
    if len(tweets) == 0:
        return

    try:
        archive = open(filename,"w")
    except IOError as e:
        err("Cannot save tweets: %s" % str(e))
        return

    for k in sorted(tweets.keys()):
        archive.write("%i %s\n" % (k, tweets[k].encode('utf-8')))

    archive.close()

def format_date(utc, isoformat=False):
    """Parse Twitter's UTC date into UTC or local time."""
    u = datetime.strptime(utc.replace('+0000','UTC'), '%a %b %d %H:%M:%S %Z %Y')
    # This is the least painful way I could find to create a non-naive
    # datetime including a UTC timezone. Alternative suggestions
    # welcome.
    unew = datetime.combine(u.date(), time(u.time().hour,
        u.time().minute, u.time().second, tzinfo=UTC))

    # Convert to localtime
    unew = unew.astimezone(Local)

    if isoformat:
        return unew.isoformat()
    else:
        return unew.strftime('%Y-%m-%d %H:%M:%S %Z')

def expand_format_text(hosts, text):
    """Following redirects in links."""
    return direct_format_text(expand_line(text, hosts))

def direct_format_text(text):
    """Transform special chars in text to have only one line."""
    return text.replace('\n','\\n').replace('\r','\\r')

def statuses_resolve_uids(twitter, tl):
    """Resolve user ids to screen names from statuses."""
    # get all user ids that needs a lookup (no screen_name key)
    user_ids = []
    for t in tl:
        rt = t.get('retweeted_status')
        if rt and not rt['user'].get('screen_name'):
            user_ids.append(rt['user']['id'])
        if not t['user'].get('screen_name'):
            user_ids.append(t['user']['id'])

    # resolve all of them at once
    names = lookup(twitter, list(set(user_ids)))

    # build new statuses with resolved uids
    new_tl = []
    for t in tl:
        rt = t.get('retweeted_status')
        if rt and not rt['user'].get('screen_name'):
            name = names[rt['user']['id']]
            t['retweeted_status']['user']['screen_name'] = name
        if not t['user'].get('screen_name'):
            name = names[t['user']['id']]
            t['user']['screen_name'] = name
        new_tl.append(t)

    return new_tl

def statuses_portion(twitter, screen_name, max_id=None, mentions=False, favorites=False, received_dms=None, isoformat=False):
    """Get a portion of the statuses of a screen name."""
    kwargs = dict(count=200, include_rts=1, screen_name=screen_name)
    if max_id:
        kwargs['max_id'] = max_id

    tweets = {}
    if mentions:
        tl = twitter.statuses.mentions_timeline(**kwargs)
    elif favorites:
        tl = twitter.favorites.list(**kwargs)
    elif received_dms != None:
        if received_dms:
            tl = twitter.direct_messages(**kwargs)
        else: # sent DMs
            tl = twitter.direct_messages.sent(**kwargs)
    else: # timeline
        if screen_name:
            tl = twitter.statuses.user_timeline(**kwargs)
        else: # self
            tl = twitter.statuses.home_timeline(**kwargs)

    # some tweets do not provide screen name but user id, resolve those
    # this isn't a valid operation for DMs, so special-case them
    if received_dms == None:
      newtl = statuses_resolve_uids(twitter, tl)
    else:
      newtl = tl
    for t in newtl:
        text = t['text']
        rt = t.get('retweeted_status')
        if rt:
            text = "RT @%s: %s" % (rt['user']['screen_name'], rt['text'])
        # DMs don't include mentions by default, so in order to show who
        # the recipient was, we synthesise a mention. If we're not
        # operating on DMs, behave as normal
        if received_dms == None:
          tweets[t['id']] = "%s <%s> %s" % (format_date(t['created_at'], isoformat=isoformat),
                                            t['user']['screen_name'],
                                            format_text(text))
        else:
          tweets[t['id']] = "%s <%s> @%s %s" % (format_date(t['created_at'], isoformat=isoformat),
                                            t['sender_screen_name'],
                                            t['recipient']['screen_name'],
                                            format_text(text))
    return tweets

def statuses(twitter, screen_name, tweets, mentions=False, favorites=False, received_dms=None, isoformat=False):
    """Get all the statuses for a screen name."""
    max_id = None
    fail = Fail()
    # get portions of statuses, incrementing max id until no new tweets appear
    while True:
        try:
            portion = statuses_portion(twitter, screen_name, max_id, mentions, favorites, received_dms, isoformat)
        except TwitterError as e:
            if e.e.code == 401:
                err("Fail: %i Unauthorized (tweets of that user are protected)"
                    % e.e.code)
                break
            elif e.e.code == 400:
                err("Fail: %i API rate limit exceeded" % e.e.code)
                rate = twitter.account.rate_limit_status()
                reset = rate['reset_time_in_seconds']
                reset = time.asctime(time.localtime(reset))
                delay = int(rate['reset_time_in_seconds']
                            - time.time()) + 5 # avoid race
                err("Hourly limit of %i requests reached, next reset on %s: "
                    "going to sleep for %i secs" % (rate['hourly_limit'],
                                                    reset, delay))
                fail.wait(delay)
                continue
            elif e.e.code == 404:
                err("Fail: %i This profile does not exist" % e.e.code)
                break
            elif e.e.code == 502:
                err("Fail: %i Service currently unavailable, retrying..."
                    % e.e.code)
            else:
                err("Fail: %s\nRetrying..." % str(e)[:500])
            fail.wait(3)
        except urllib2.URLError as e:
            err("Fail: urllib2.URLError %s - Retrying..." % str(e))
            fail.wait(3)
        except httplib.error as e:
            err("Fail: httplib.error %s - Retrying..." % str(e))
            fail.wait(3)
        except KeyError as e:
            err("Fail: KeyError %s - Retrying..." % str(e))
            fail.wait(3)
        else:
            new = -len(tweets)
            tweets.update(portion)
            new += len(tweets)
            err("Browsing %s statuses, new tweets: %i"
                % (screen_name if screen_name else "home", new))
            if new < 190:
                break
            max_id = min(portion.keys())-1 # browse backwards
            fail = Fail()

def rate_limit_status(twitter):
    """Print current Twitter API rate limit status."""
    r = twitter.account.rate_limit_status()
    print("Remaining API requests: %i/%i (hourly limit)"
          % (r['remaining_hits'], r['hourly_limit']))
    print("Next reset in %is (%s)"
          % (int(r['reset_time_in_seconds'] - time.time()),
             time.asctime(time.localtime(r['reset_time_in_seconds']))))

def main(args=sys.argv[1:]):
    options = {
        'oauth': False,
        'save-dir': ".",
        'api-rate': False,
        'timeline': "",
        'mentions': "",
        'dms': "",
        'favorites': False,
        'follow-redirects': False,
        'redirect-sites': None,
        'isoformat': False,
    }
    try:
        parse_args(args, options)
    except GetoptError as e:
        err("I can't do that, %s." % e)
        raise SystemExit(1)

    # exit if no user given
    # except if asking for API rate, or archive of timeline or mentions
    if not options['extra_args'] and not (options['api-rate'] or
                                          options['timeline'] or
                                          options['mentions'] or
                                          options['dms']):
        print(__doc__)
        return

    # authenticate using OAuth, asking for token if necessary
    if options['oauth']:
        oauth_filename = (os.getenv("HOME", "") + os.sep
                          + ".twitter-archiver_oauth")
        if not os.path.exists(oauth_filename):
            oauth_dance("Twitter-Archiver", CONSUMER_KEY, CONSUMER_SECRET,
                        oauth_filename)
        oauth_token, oauth_token_secret = read_token_file(oauth_filename)
        auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY,
                     CONSUMER_SECRET)
    else:
        auth = NoAuth()

    twitter = Twitter(auth=auth, api_version='1.1', domain='api.twitter.com')

    if options['api-rate']:
        rate_limit_status(twitter)
        return

    global format_text
    if options['follow-redirects'] or options['redirect-sites'] :
        if options['redirect-sites']:
            hosts = parse_host_list(options['redirect-sites'])
        else:
            hosts = None
        format_text = functools.partial(expand_format_text, hosts)
    else:
        format_text = direct_format_text

    # save own timeline or mentions (the user used in OAuth)
    if options['timeline'] or options['mentions']:
        if isinstance(auth, NoAuth):
            err("You must be authenticated to save timeline or mentions.")
            raise SystemExit(1)

        if options['timeline']:
            filename = options['save-dir'] + os.sep + options['timeline']
            print("* Archiving own timeline in %s" % filename)
        elif options['mentions']:
            filename = options['save-dir'] + os.sep + options['mentions']
            print("* Archiving own mentions in %s" % filename)

        tweets = {}
        try:
            tweets = load_tweets(filename)
        except Exception as e:
            err("Error when loading saved tweets: %s - continuing without"
                % str(e))

        try:
            statuses(twitter, "", tweets, options['mentions'], options['favorites'], isoformat=options['isoformat'])
        except KeyboardInterrupt:
            err()
            err("Interrupted")
            raise SystemExit(1)

        save_tweets(filename, tweets)
        if options['timeline']:
            print("Total tweets in own timeline: %i" % len(tweets))
        elif options['mentions']:
            print("Total mentions: %i" % len(tweets))

    if options['dms']:
        if isinstance(auth, NoAuth):
            err("You must be authenticated to save DMs.")
            raise SystemExit(1)

        filename = options['save-dir'] + os.sep + options['dms']
        print("* Archiving own DMs in %s" % filename)

        dms = {}
        try:
            dms = load_tweets(filename)
        except Exception as e:
            err("Error when loading saved DMs: %s - continuing without"
                % str(e))

        try:
            statuses(twitter, "", dms, received_dms=True, isoformat=options['isoformat'])
            statuses(twitter, "", dms, received_dms=False, isoformat=options['isoformat'])
        except KeyboardInterrupt:
            err()
            err("Interrupted")
            raise SystemExit(1)

        save_tweets(filename, dms)
        print("Total DMs sent and received: %i" % len(dms))


    # read users from command-line or stdin
    users = options['extra_args']
    if len(users) == 1 and users[0] == "-":
        users = [line.strip() for line in sys.stdin.readlines()]

    # save tweets for every user
    total, total_new = 0, 0
    for user in users:
        filename = options['save-dir'] + os.sep + user
        if options['favorites']:
            filename = filename + "-favorites"
        print("* Archiving %s tweets in %s" % (user, filename))

        tweets = {}
        try:
            tweets = load_tweets(filename)
        except Exception as e:
            err("Error when loading saved tweets: %s - continuing without"
                % str(e))

        new = 0
        before = len(tweets)
        try:
            statuses(twitter, user, tweets, options['mentions'], options['favorites'], isoformat=options['isoformat'])
        except KeyboardInterrupt:
            err()
            err("Interrupted")
            raise SystemExit(1)

        save_tweets(filename, tweets)
        total += len(tweets)
        new = len(tweets) - before
        total_new += new
        print("Total tweets for %s: %i (%i new)" % (user, len(tweets), new))

    print("Total: %i tweets (%i new) for %i users"
          % (total, total_new, len(users)))

########NEW FILE########
__FILENAME__ = auth
try:
    import urllib.parse as urllib_parse
    from base64 import encodebytes
except ImportError:
    import urllib as urllib_parse
    from base64 import encodestring as encodebytes

class Auth(object):
    """
    ABC for Authenticator objects.
    """

    def encode_params(self, base_url, method, params):
        """Encodes parameters for a request suitable for including in a URL
        or POST body.  This method may also add new params to the request
        if required by the authentication scheme in use."""
        raise NotImplementedError()

    def generate_headers(self):
        """Generates headers which should be added to the request if required
        by the authentication scheme in use."""
        raise NotImplementedError()

class UserPassAuth(Auth):
    """
    Basic auth authentication using email/username and
    password. Deprecated.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def encode_params(self, base_url, method, params):
        # We could consider automatically converting unicode to utf8 strings
        # before encoding...
        return urllib_parse.urlencode(params)

    def generate_headers(self):
        return {b"Authorization": b"Basic " + encodebytes(
                ("%s:%s" %(self.username, self.password))
                .encode('utf8')).strip(b'\n')
                }

class NoAuth(Auth):
    """
    No authentication authenticator.
    """
    def __init__(self):
        pass

    def encode_params(self, base_url, method, params):
        return urllib_parse.urlencode(params)

    def generate_headers(self):
        return {}

########NEW FILE########
__FILENAME__ = cmdline
# encoding: utf-8
"""
USAGE:

 twitter [action] [options]


ACTIONS:
 authorize      authorize the command-line tool to interact with Twitter
 follow         follow a user
 friends        get latest tweets from your friends (default action)
 help           print this help text that you are currently reading
 leave          stop following a user
 list           get list of a user's lists; give a list name to get
                    tweets from that list
 mylist         get list of your lists; give a list name to get tweets
                    from that list
 pyprompt       start a Python prompt for interacting with the twitter
                    object directly
 replies        get latest replies to you
 search         search twitter (Beware: octothorpe, escape it)
 set            set your twitter status
 shell          login to the twitter shell
 rate           get your current rate limit status (remaining API reqs)


OPTIONS:

 -r --refresh               run this command forever, polling every once
                            in a while (default: every 5 minutes)
 -R --refresh-rate <rate>   set the refresh rate (in seconds)
 -f --format <format>       specify the output format for status updates
 -c --config <filename>     read username and password from given config
                            file (default ~/.twitter)
 -l --length <count>        specify number of status updates shown
                            (default: 20, max: 200)
 -t --timestamp             show time before status lines
 -d --datestamp             show date before status lines
    --no-ssl                use less-secure HTTP instead of HTTPS
    --oauth <filename>      filename to read/store oauth credentials to

FORMATS for the --format option

 default         one line per status
 verbose         multiple lines per status, more verbose status info
 json            raw json data from the api on each line
 urls            nothing but URLs
 ansi            ansi colour (rainbow mode)


CONFIG FILES

 The config file should be placed in your home directory and be named .twitter.
 It must contain a [twitter] header, and all the desired options you wish to
 set, like so:

[twitter]
format: <desired_default_format_for_output>
prompt: <twitter_shell_prompt e.g. '[cyan]twitter[R]> '>

 OAuth authentication tokens are stored in the file .twitter_oauth in your
 home directory.
"""

from __future__ import print_function

try:
    input = __builtins__['raw_input']
except (AttributeError, KeyError):
    pass


CONSUMER_KEY = 'uS6hO2sV6tDKIOeVjhnFnQ'
CONSUMER_SECRET = 'MEYTOS97VvlHX7K1rwHPEqVpTSqZ71HtvoK4sVuYk'

from getopt import gnu_getopt as getopt, GetoptError
from getpass import getpass
import json
import locale
import os.path
import re
import string
import sys
import time

try:
    from ConfigParser import SafeConfigParser
except ImportError:
    from configparser import ConfigParser as SafeConfigParser
import datetime
try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote
try:
    import HTMLParser
except ImportError:
    import html.parser as HTMLParser

import webbrowser

from .api import Twitter, TwitterError
from .oauth import OAuth, write_token_file, read_token_file
from .oauth_dance import oauth_dance
from . import ansi
from .util import smrt_input, printNicely

OPTIONS = {
    'action': 'friends',
    'refresh': False,
    'refresh_rate': 600,
    'format': 'default',
    'prompt': '[cyan]twitter[R]> ',
    'config_filename': os.environ.get('HOME', os.environ.get('USERPROFILE', '')) + os.sep + '.twitter',
    'oauth_filename': os.environ.get('HOME', os.environ.get('USERPROFILE', '')) + os.sep + '.twitter_oauth',
    'length': 20,
    'timestamp': False,
    'datestamp': False,
    'extra_args': [],
    'secure': True,
    'invert_split': False,
    'force-ansi': False,
}

gHtmlParser = HTMLParser.HTMLParser()
hashtagRe = re.compile(r'(?P<hashtag>#\S+)')
profileRe = re.compile(r'(?P<profile>\@\S+)')
ansiFormatter = ansi.AnsiCmd(False)

def parse_args(args, options):
    long_opts = ['help', 'format=', 'refresh', 'oauth=',
                 'refresh-rate=', 'config=', 'length=', 'timestamp',
                 'datestamp', 'no-ssl', 'force-ansi']
    short_opts = "e:p:f:h?rR:c:l:td"
    opts, extra_args = getopt(args, short_opts, long_opts)
    if extra_args and hasattr(extra_args[0], 'decode'):
        extra_args = [arg.decode(locale.getpreferredencoding())
                      for arg in extra_args]

    for opt, arg in opts:
        if opt in ('-f', '--format'):
            options['format'] = arg
        elif opt in ('-r', '--refresh'):
            options['refresh'] = True
        elif opt in ('-R', '--refresh-rate'):
            options['refresh_rate'] = int(arg)
        elif opt in ('-l', '--length'):
            options["length"] = int(arg)
        elif opt in ('-t', '--timestamp'):
            options["timestamp"] = True
        elif opt in ('-d', '--datestamp'):
            options["datestamp"] = True
        elif opt in ('-?', '-h', '--help'):
            options['action'] = 'help'
        elif opt in ('-c', '--config'):
            options['config_filename'] = arg
        elif opt == '--no-ssl':
            options['secure'] = False
        elif opt == '--oauth':
            options['oauth_filename'] = arg
        elif opt == '--force-ansi':
            options['force-ansi'] = True

    if extra_args and not ('action' in options and options['action'] == 'help'):
        options['action'] = extra_args[0]
    options['extra_args'] = extra_args[1:]

def get_time_string(status, options, format="%a %b %d %H:%M:%S +0000 %Y"):
    timestamp = options["timestamp"]
    datestamp = options["datestamp"]
    t = time.strptime(status['created_at'], format)
    i_hate_timezones = time.timezone
    if (time.daylight):
        i_hate_timezones = time.altzone
    dt = datetime.datetime(*t[:-3]) - datetime.timedelta(
        seconds=i_hate_timezones)
    t = dt.timetuple()
    if timestamp and datestamp:
        return time.strftime("%Y-%m-%d %H:%M:%S ", t)
    elif timestamp:
        return time.strftime("%H:%M:%S ", t)
    elif datestamp:
        return time.strftime("%Y-%m-%d ", t)
    return ""

def reRepl(m):
    ansiTypes = {
          'clear':   ansiFormatter.cmdReset(),
          'hashtag': ansiFormatter.cmdBold(),
          'profile': ansiFormatter.cmdUnderline(),
          }

    s = None
    try:
        mkey = m.lastgroup
        if m.group(mkey):
            s = '%s%s%s' % (ansiTypes[mkey], m.group(mkey), ansiTypes['clear'])
    except IndexError:
        pass
    return s

def replaceInStatus(status):
    txt = gHtmlParser.unescape(status)
    txt = re.sub(hashtagRe, reRepl, txt)
    txt = re.sub(profileRe, reRepl, txt)
    return txt

class StatusFormatter(object):
    def __call__(self, status, options):
        return ("%s%s %s" % (
            get_time_string(status, options),
            status['user']['screen_name'], gHtmlParser.unescape(status['text'])))

class AnsiStatusFormatter(object):
    def __init__(self):
        self._colourMap = ansi.ColourMap()

    def __call__(self, status, options):
        colour = self._colourMap.colourFor(status['user']['screen_name'])
        return ("%s%s%s%s %s" % (
            get_time_string(status, options),
            ansiFormatter.cmdColour(colour), status['user']['screen_name'],
            ansiFormatter.cmdReset(), replaceInStatus(status['text'])))

class VerboseStatusFormatter(object):
    def __call__(self, status, options):
        return ("-- %s (%s) on %s\n%s\n" % (
            status['user']['screen_name'],
            status['user']['location'],
            status['created_at'],
            gHtmlParser.unescape(status['text'])))

class JSONStatusFormatter(object):
    def __call__(self, status, options):
         status['text'] = gHtmlParser.unescape(status['text'])
         return json.dumps(status)

class URLStatusFormatter(object):
    urlmatch = re.compile(r'https?://\S+')
    def __call__(self, status, options):
        urls = self.urlmatch.findall(status['text'])
        return '\n'.join(urls) if urls else ""


class ListsFormatter(object):
    def __call__(self, list):
        if list['description']:
            list_str = "%-30s (%s)" % (list['name'], list['description'])
        else:
            list_str = "%-30s" % (list['name'])
        return "%s\n" % list_str

class ListsVerboseFormatter(object):
    def __call__(self, list):
        list_str = "%-30s\n description: %s\n members: %s\n mode:%s\n" % (list['name'], list['description'], list['member_count'], list['mode'])
        return list_str

class AnsiListsFormatter(object):
    def __init__(self):
        self._colourMap = ansi.ColourMap()

    def __call__(self, list):
        colour = self._colourMap.colourFor(list['name'])
        return ("%s%-15s%s %s" % (
            ansiFormatter.cmdColour(colour), list['name'],
            ansiFormatter.cmdReset(), list['description']))


class AdminFormatter(object):
    def __call__(self, action, user):
        user_str = "%s (%s)" % (user['screen_name'], user['name'])
        if action == "follow":
            return "You are now following %s.\n" % (user_str)
        else:
            return "You are no longer following %s.\n" % (user_str)

class VerboseAdminFormatter(object):
    def __call__(self, action, user):
        return("-- %s: %s (%s): %s" % (
            "Following" if action == "follow" else "Leaving",
            user['screen_name'],
            user['name'],
            user['url']))

class SearchFormatter(object):
    def __call__(self, result, options):
        return("%s%s %s" % (
            get_time_string(result, options, "%a, %d %b %Y %H:%M:%S +0000"),
            result['from_user'], result['text']))

class VerboseSearchFormatter(SearchFormatter):
    pass  # Default to the regular one

class URLSearchFormatter(object):
    urlmatch = re.compile(r'https?://\S+')
    def __call__(self, result, options):
        urls = self.urlmatch.findall(result['text'])
        return '\n'.join(urls) if urls else ""

class AnsiSearchFormatter(object):
    def __init__(self):
        self._colourMap = ansi.ColourMap()

    def __call__(self, result, options):
        colour = self._colourMap.colourFor(result['from_user'])
        return ("%s%s%s%s %s" % (
            get_time_string(result, options, "%a, %d %b %Y %H:%M:%S +0000"),
            ansiFormatter.cmdColour(colour), result['from_user'],
            ansiFormatter.cmdReset(), result['text']))

_term_encoding = None
def get_term_encoding():
    global _term_encoding
    if not _term_encoding:
        lang = os.getenv('LANG', 'unknown.UTF-8').split('.')
        if lang[1:]:
            _term_encoding = lang[1]
        else:
            _term_encoding = 'UTF-8'
    return _term_encoding

formatters = {}
status_formatters = {
    'default': StatusFormatter,
    'verbose': VerboseStatusFormatter,
    'json': JSONStatusFormatter,
    'urls': URLStatusFormatter,
    'ansi': AnsiStatusFormatter
}
formatters['status'] = status_formatters

admin_formatters = {
    'default': AdminFormatter,
    'verbose': VerboseAdminFormatter,
    'urls': AdminFormatter,
    'ansi': AdminFormatter
}
formatters['admin'] = admin_formatters

search_formatters = {
    'default': SearchFormatter,
    'verbose': VerboseSearchFormatter,
    'urls': URLSearchFormatter,
    'ansi': AnsiSearchFormatter
}
formatters['search'] = search_formatters

lists_formatters = {
    'default': ListsFormatter,
    'verbose': ListsVerboseFormatter,
    'urls': None,
    'ansi': AnsiListsFormatter
}
formatters['lists'] = lists_formatters

def get_formatter(action_type, options):
    formatters_dict = formatters.get(action_type)
    if (not formatters_dict):
        raise TwitterError(
            "There was an error finding a class of formatters for your type (%s)"
            % (action_type))
    f = formatters_dict.get(options['format'])
    if (not f):
        raise TwitterError(
            "Unknown formatter '%s' for status actions" % (options['format']))
    return f()

class Action(object):

    def ask(self, subject='perform this action', careful=False):
        '''
        Requests fromt he user using `raw_input` if `subject` should be
        performed. When `careful`, the default answer is NO, otherwise YES.
        Returns the user answer in the form `True` or `False`.
        '''
        sample = '(y/N)'
        if not careful:
            sample = '(Y/n)'

        prompt = 'You really want to %s %s? ' % (subject, sample)
        try:
            answer = input(prompt).lower()
            if careful:
                return answer in ('yes', 'y')
            else:
                return answer not in ('no', 'n')
        except EOFError:
            print(file=sys.stderr)  # Put Newline since Enter was never pressed
            # TODO:
                #   Figure out why on OS X the raw_input keeps raising
                #   EOFError and is never able to reset and get more input
                #   Hint: Look at how IPython implements their console
            default = True
            if careful:
                default = False
            return default

    def __call__(self, twitter, options):
        action = actions.get(options['action'], NoSuchAction)()
        try:
            doAction = lambda : action(twitter, options)
            if (options['refresh'] and isinstance(action, StatusAction)):
                while True:
                    doAction()
                    sys.stdout.flush()
                    time.sleep(options['refresh_rate'])
            else:
                doAction()
        except KeyboardInterrupt:
            print('\n[Keyboard Interrupt]', file=sys.stderr)
            pass

class NoSuchActionError(Exception):
    pass

class NoSuchAction(Action):
    def __call__(self, twitter, options):
        raise NoSuchActionError("No such action: %s" % (options['action']))

class StatusAction(Action):
    def __call__(self, twitter, options):
        statuses = self.getStatuses(twitter, options)
        sf = get_formatter('status', options)
        for status in statuses:
            statusStr = sf(status, options)
            if statusStr.strip():
                printNicely(statusStr)

class SearchAction(Action):
    def __call__(self, twitter, options):
        # We need to be pointing at search.twitter.com to work, and it is less
        # tangly to do it here than in the main()
        twitter.domain = "search.twitter.com"
        twitter.uriparts = ()
        # We need to bypass the TwitterCall parameter encoding, so we
        # don't encode the plus sign, so we have to encode it ourselves
        query_string = "+".join(
            [quote(term)
             for term in options['extra_args']])

        results = twitter.search(q=query_string)['results']
        f = get_formatter('search', options)
        for result in results:
            resultStr = f(result, options)
            if resultStr.strip():
                printNicely(resultStr)

class AdminAction(Action):
    def __call__(self, twitter, options):
        if not (options['extra_args'] and options['extra_args'][0]):
            raise TwitterError("You need to specify a user (screen name)")
        af = get_formatter('admin', options)
        try:
            user = self.getUser(twitter, options['extra_args'][0])
        except TwitterError as e:
            print("There was a problem following or leaving the specified user.")
            print("You may be trying to follow a user you are already following;")
            print("Leaving a user you are not currently following;")
            print("Or the user may not exist.")
            print("Sorry.")
            print()
            print(e)
        else:
            printNicely(af(options['action'], user))

class ListsAction(StatusAction):
    def getStatuses(self, twitter, options):
        if not options['extra_args']:
            raise TwitterError("Please provide a user to query for lists")

        screen_name = options['extra_args'][0]

        if not options['extra_args'][1:]:
            lists = twitter.lists.list(screen_name=screen_name)
            if not lists:
                printNicely("This user has no lists.")
            for list in lists:
                lf = get_formatter('lists', options)
                printNicely(lf(list))
            return []
        else:
            return reversed(twitter.user.lists.list.statuses(
                    user=screen_name, list=options['extra_args'][1]))


class MyListsAction(ListsAction):
    def getStatuses(self, twitter, options):
        screen_name = twitter.account.verify_credentials()['screen_name']
        options['extra_args'].insert(0, screen_name)
        return ListsAction.getStatuses(self, twitter, options)


class FriendsAction(StatusAction):
    def getStatuses(self, twitter, options):
        return reversed(twitter.statuses.home_timeline(count=options["length"]))

class RepliesAction(StatusAction):
    def getStatuses(self, twitter, options):
        return reversed(twitter.statuses.mentions_timeline(count=options["length"]))

class FollowAction(AdminAction):
    def getUser(self, twitter, user):
        return twitter.friendships.create(screen_name=user)

class LeaveAction(AdminAction):
    def getUser(self, twitter, user):
        return twitter.friendships.destroy(screen_name=user)

class SetStatusAction(Action):
    def __call__(self, twitter, options):
        statusTxt = (" ".join(options['extra_args'])
                     if options['extra_args']
                     else str(input("message: ")))
        replies = []
        ptr = re.compile("@[\w_]+")
        while statusTxt:
            s = ptr.match(statusTxt)
            if s and s.start() == 0:
                replies.append(statusTxt[s.start():s.end()])
                statusTxt = statusTxt[s.end() + 1:]
            else:
                break
        replies = " ".join(replies)
        if len(replies) >= 140:
            # just go back
            statusTxt = replies
            replies = ""

        splitted = []
        while statusTxt:
            limit = 140 - len(replies)
            if len(statusTxt) > limit:
                end = string.rfind(statusTxt, ' ', 0, limit)
            else:
                end = limit
            splitted.append(" ".join((replies, statusTxt[:end])))
            statusTxt = statusTxt[end:]

        if options['invert_split']:
            splitted.reverse()
        for status in splitted:
            twitter.statuses.update(status=status)

class TwitterShell(Action):

    def render_prompt(self, prompt):
        '''Parses the `prompt` string and returns the rendered version'''
        prompt = prompt.strip("'").replace("\\'", "'")
        for colour in ansi.COLOURS_NAMED:
            if '[%s]' % (colour) in prompt:
                prompt = prompt.replace(
                    '[%s]' % (colour), ansiFormatter.cmdColourNamed(colour))
        prompt = prompt.replace('[R]', ansiFormatter.cmdReset())
        return prompt

    def __call__(self, twitter, options):
        prompt = self.render_prompt(options.get('prompt', 'twitter> '))
        while True:
            options['action'] = ""
            try:
                args = input(prompt).split()
                parse_args(args, options)
                if not options['action']:
                    continue
                elif options['action'] == 'exit':
                    raise SystemExit(0)
                elif options['action'] == 'shell':
                    print('Sorry Xzibit does not work here!', file=sys.stderr)
                    continue
                elif options['action'] == 'help':
                    print('''\ntwitter> `action`\n
                          The Shell Accepts all the command line actions along with:

                          exit    Leave the twitter shell (^D may also be used)

                          Full CMD Line help is appended below for your convinience.''', file=sys.stderr)
                Action()(twitter, options)
                options['action'] = ''
            except NoSuchActionError as e:
                print(e, file=sys.stderr)
            except KeyboardInterrupt:
                print('\n[Keyboard Interrupt]', file=sys.stderr)
            except EOFError:
                print(file=sys.stderr)
                leaving = self.ask(subject='Leave')
                if not leaving:
                    print('Excellent!', file=sys.stderr)
                else:
                    raise SystemExit(0)

class PythonPromptAction(Action):
    def __call__(self, twitter, options):
        try:
            while True:
                smrt_input(globals(), locals())
        except EOFError:
            pass

class HelpAction(Action):
    def __call__(self, twitter, options):
        print(__doc__)

class DoNothingAction(Action):
    def __call__(self, twitter, options):
        pass

class RateLimitStatus(Action):
    def __call__(self, twitter, options):
        rate = twitter.account.rate_limit_status()
        print("Remaining API requests: %s / %s (hourly limit)" % (rate['remaining_hits'], rate['hourly_limit']))
        print("Next reset in %ss (%s)" % (int(rate['reset_time_in_seconds'] - time.time()),
                                          time.asctime(time.localtime(rate['reset_time_in_seconds']))))

actions = {
    'authorize' : DoNothingAction,
    'follow'    : FollowAction,
    'friends'   : FriendsAction,
    'list'      : ListsAction,
    'mylist'    : MyListsAction,
    'help'      : HelpAction,
    'leave'     : LeaveAction,
    'pyprompt'  : PythonPromptAction,
    'replies'   : RepliesAction,
    'search'    : SearchAction,
    'set'       : SetStatusAction,
    'shell'     : TwitterShell,
    'rate'      : RateLimitStatus,
}

def loadConfig(filename):
    options = dict(OPTIONS)
    if os.path.exists(filename):
        cp = SafeConfigParser()
        cp.read([filename])
        for option in ('format', 'prompt'):
            if cp.has_option('twitter', option):
                options[option] = cp.get('twitter', option)
        # process booleans
        for option in ('invert_split',):
            if cp.has_option('twitter', option):
                options[option] = cp.getboolean('twitter', option)
    return options

def main(args=sys.argv[1:]):
    arg_options = {}
    try:
        parse_args(args, arg_options)
    except GetoptError as e:
        print("I can't do that, %s." % (e), file=sys.stderr)
        print(file=sys.stderr)
        raise SystemExit(1)

    config_path = os.path.expanduser(
        arg_options.get('config_filename') or OPTIONS.get('config_filename'))
    config_options = loadConfig(config_path)

    # Apply the various options in order, the most important applied last.
    # Defaults first, then what's read from config file, then command-line
    # arguments.
    options = dict(OPTIONS)
    for d in config_options, arg_options:
        for k, v in list(d.items()):
            if v: options[k] = v

    if options['refresh'] and options['action'] not in (
        'friends', 'replies'):
        print("You can only refresh the friends or replies actions.", file=sys.stderr)
        print("Use 'twitter -h' for help.", file=sys.stderr)
        return 1

    oauth_filename = os.path.expanduser(options['oauth_filename'])

    if (options['action'] == 'authorize'
        or not os.path.exists(oauth_filename)):
        oauth_dance(
            "the Command-Line Tool", CONSUMER_KEY, CONSUMER_SECRET,
            options['oauth_filename'])

    global ansiFormatter
    ansiFormatter = ansi.AnsiCmd(options["force-ansi"])

    oauth_token, oauth_token_secret = read_token_file(oauth_filename)

    twitter = Twitter(
        auth=OAuth(
            oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        secure=options['secure'],
        api_version='1.1',
        domain='api.twitter.com')

    try:
        Action()(twitter, options)
    except NoSuchActionError as e:
        print(e, file=sys.stderr)
        raise SystemExit(1)
    except TwitterError as e:
        print(str(e), file=sys.stderr)
        print("Use 'twitter -h' for help.", file=sys.stderr)
        raise SystemExit(1)

########NEW FILE########
__FILENAME__ = follow
"""USAGE
    twitter-follow [options] <user>

DESCRIPTION
    Display all following/followers of a user, one user per line.

OPTIONS
 -o --oauth            authenticate to Twitter using OAuth (default no)
 -r --followers        display followers of the given user (default)
 -g --following        display users the given user is following
 -a --api-rate         see your current API rate limit status
 -i --ids              prepend user id to each line. useful to tracking renames

AUTHENTICATION
    Authenticate to Twitter using OAuth to see following/followers of private
    profiles and have higher API rate limits. OAuth authentication tokens
    are stored in the file .twitter-follow_oauth in your home directory.
"""

from __future__ import print_function

import os, sys, time, calendar
from getopt import gnu_getopt as getopt, GetoptError

try:
    import urllib.request as urllib2
    import http.client as httplib
except ImportError:
    import urllib2
    import httplib

# T-Follow (Twitter-Follow) application registered by @stalkr_
CONSUMER_KEY='USRZQfvFFjB6UvZIN2Edww'
CONSUMER_SECRET='AwGAaSzZa5r0TDL8RKCDtffnI9H9mooZUdOa95nw8'

from .api import Twitter, TwitterError
from .oauth import OAuth, read_token_file
from .oauth_dance import oauth_dance
from .auth import NoAuth
from .util import Fail, err


def parse_args(args, options):
    """Parse arguments from command-line to set options."""
    long_opts = ['help', 'oauth', 'followers', 'following', 'api-rate', 'ids']
    short_opts = "horgai"
    opts, extra_args = getopt(args, short_opts, long_opts)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            raise SystemExit(1)
        elif opt in ('-o', '--oauth'):
            options['oauth'] = True
        elif opt in ('-r', '--followers'):
            options['followers'] = True
        elif opt in ('-g', '--following'):
            options['followers'] = False
        elif opt in ('-a', '--api-rate'):
            options['api-rate' ] = True
        elif opt in ('-i', '--ids'):
            options['show_id'] = True

    options['extra_args'] = extra_args

def lookup_portion(twitter, user_ids):
    """Resolve a limited list of user ids to screen names."""
    users = {}
    kwargs = dict(user_id=",".join(map(str, user_ids)), skip_status=1)
    for u in twitter.users.lookup(**kwargs):
        users[int(u['id'])] = u['screen_name']
    return users

def lookup(twitter, user_ids):
    """Resolve an entire list of user ids to screen names."""
    users = {}
    api_limit = 100
    for i in range(0, len(user_ids), api_limit):
        fail = Fail()
        while True:
            try:
                portion = lookup_portion(twitter, user_ids[i:][:api_limit])
            except TwitterError as e:
                if e.e.code == 400:
                    err("Fail: %i API rate limit exceeded" % e.e.code)
                    rate = twitter.account.rate_limit_status()
                    reset = rate['reset_time_in_seconds']
                    reset = time.asctime(time.localtime(reset))
                    delay = int(rate['reset_time_in_seconds']
                                - time.time()) + 5 # avoid race
                    err("Hourly limit of %i requests reached, next reset on "
                        "%s: going to sleep for %i secs"
                        % (rate['hourly_limit'], reset, delay))
                    fail.wait(delay)
                    continue
                elif e.e.code == 502:
                    err("Fail: %i Service currently unavailable, retrying..."
                        % e.e.code)
                else:
                    err("Fail: %s\nRetrying..." % str(e)[:500])
                fail.wait(3)
            except urllib2.URLError as e:
                err("Fail: urllib2.URLError %s - Retrying..." % str(e))
                fail.wait(3)
            except httplib.error as e:
                err("Fail: httplib.error %s - Retrying..." % str(e))
                fail.wait(3)
            except KeyError as e:
                err("Fail: KeyError %s - Retrying..." % str(e))
                fail.wait(3)
            else:
                users.update(portion)
                err("Resolving user ids to screen names: %i/%i"
                    % (len(users), len(user_ids)))
                break
    return users

def follow_portion(twitter, screen_name, cursor=-1, followers=True):
    """Get a portion of followers/following for a user."""
    kwargs = dict(screen_name=screen_name, cursor=cursor)
    if followers:
        t = twitter.followers.ids(**kwargs)
    else: # following
        t = twitter.friends.ids(**kwargs)
    return t['ids'], t['next_cursor']

def follow(twitter, screen_name, followers=True):
    """Get the entire list of followers/following for a user."""
    user_ids = []
    cursor = -1
    fail = Fail()
    while True:
        try:
            portion, cursor = follow_portion(twitter, screen_name, cursor,
                                             followers)
        except TwitterError as e:
            if e.e.code == 401:
                reason = ("follow%s of that user are protected"
                          % ("ers" if followers else "ing"))
                err("Fail: %i Unauthorized (%s)" % (e.e.code, reason))
                break
            elif e.e.code == 400:
                err("Fail: %i API rate limit exceeded" % e.e.code)
                rate = twitter.account.rate_limit_status()
                reset = rate['reset_time_in_seconds']
                reset = time.asctime(time.localtime(reset))
                delay = int(rate['reset_time_in_seconds']
                            - time.time()) + 5 # avoid race
                err("Hourly limit of %i requests reached, next reset on %s: "
                    "going to sleep for %i secs" % (rate['hourly_limit'],
                                                    reset, delay))
                fail.wait(delay)
                continue
            elif e.e.code == 502:
                err("Fail: %i Service currently unavailable, retrying..."
                    % e.e.code)
            else:
                err("Fail: %s\nRetrying..." % str(e)[:500])
            fail.wait(3)
        except urllib2.URLError as e:
            err("Fail: urllib2.URLError %s - Retrying..." % str(e))
            fail.wait(3)
        except httplib.error as e:
            err("Fail: httplib.error %s - Retrying..." % str(e))
            fail.wait(3)
        except KeyError as e:
            err("Fail: KeyError %s - Retrying..." % str(e))
            fail.wait(3)
        else:
            new = -len(user_ids)
            user_ids = list(set(user_ids + portion))
            new += len(user_ids)
            what = "follow%s" % ("ers" if followers else "ing")
            err("Browsing %s %s, new: %i" % (screen_name, what, new))
            if cursor == 0:
                break
            fail = Fail()
    return user_ids


def rate_limit_status(twitter):
    """Print current Twitter API rate limit status."""
    r = twitter.account.rate_limit_status()
    print("Remaining API requests: %i/%i (hourly limit)"
          % (r['remaining_hits'], r['hourly_limit']))
    print("Next reset in %is (%s)"
          % (int(r['reset_time_in_seconds'] - time.time()),
             time.asctime(time.localtime(r['reset_time_in_seconds']))))

def main(args=sys.argv[1:]):
    options = {
        'oauth': False,
        'followers': True,
        'api-rate': False,
        'show_id': False
    }
    try:
        parse_args(args, options)
    except GetoptError as e:
        err("I can't do that, %s." % e)
        raise SystemExit(1)

    # exit if no user or given, except if asking for API rate
    if not options['extra_args'] and not options['api-rate']:
        print(__doc__)
        raise SystemExit(1)

    # authenticate using OAuth, asking for token if necessary
    if options['oauth']:
        oauth_filename = (os.getenv("HOME", "") + os.sep
                          + ".twitter-follow_oauth")
        if not os.path.exists(oauth_filename):
            oauth_dance("Twitter-Follow", CONSUMER_KEY, CONSUMER_SECRET,
                        oauth_filename)
        oauth_token, oauth_token_secret = read_token_file(oauth_filename)
        auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY,
                     CONSUMER_SECRET)
    else:
        auth = NoAuth()

    twitter = Twitter(auth=auth, api_version='1.1', domain='api.twitter.com')

    if options['api-rate']:
        rate_limit_status(twitter)
        return

    # obtain list of followers (or following) for every given user
    for user in options['extra_args']:
        user_ids, users = [], {}
        try:
            user_ids = follow(twitter, user, options['followers'])
            users = lookup(twitter, user_ids)
        except KeyboardInterrupt as e:
            err()
            err("Interrupted.")
            raise SystemExit(1)

        for uid in user_ids:
            if options['show_id']:
              try:
                print(str(uid) + "\t" + users[uid].encode("utf-8"))
              except KeyError:
                pass
            
            else:
              try:
                print(users[uid].encode("utf-8"))
              except KeyError:
                pass

        # print total on stderr to separate from user list on stdout
        if options['followers']:
            err("Total followers for %s: %i" % (user, len(user_ids)))
        else:
            err("Total users %s is following: %i" % (user, len(user_ids)))

########NEW FILE########
__FILENAME__ = ircbot
"""
twitterbot

  A twitter IRC bot. Twitterbot connected to an IRC server and idles in
  a channel, polling a twitter account and broadcasting all updates to
  friends.

USAGE

  twitterbot [config_file]

CONFIG_FILE

  The config file is an ini-style file that must contain the following:

[irc]
server: <irc_server>
port: <irc_port>
nick: <irc_nickname>
channel: <irc_channels_to_join>
prefixes: <prefix_type>

[twitter]
oauth_token_file: <oauth_token_filename>


  If no config file is given "twitterbot.ini" will be used by default.

  The channel argument can accept multiple channels separated by commas.

  The default token file is ~/.twitterbot_oauth.

  The default prefix type is 'cats'. You can also use 'none'.

"""

from __future__ import print_function

BOT_VERSION = "TwitterBot 1.9.1 (http://mike.verdone.ca/twitter)"

CONSUMER_KEY = "XryIxN3J2ACaJs50EizfLQ"
CONSUMER_SECRET = "j7IuDCNjftVY8DBauRdqXs4jDl5Fgk1IJRag8iE"

IRC_BOLD = chr(0x02)
IRC_ITALIC = chr(0x16)
IRC_UNDERLINE = chr(0x1f)
IRC_REGULAR = chr(0x0f)

import sys
import time
from datetime import datetime, timedelta
from email.utils import parsedate
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
from heapq import heappop, heappush
import traceback
import os
import os.path

from .api import Twitter, TwitterError
from .oauth import OAuth, read_token_file
from .oauth_dance import oauth_dance
from .util import htmlentitydecode

PREFIXES = dict(
    cats=dict(
        new_tweet="=^_^= ",
        error="=O_o= ",
        inform="=o_o= "
        ),
    none=dict(
        new_tweet=""
        ),
    )
ACTIVE_PREFIXES=dict()

def get_prefix(prefix_typ=None):
    return ACTIVE_PREFIXES.get(prefix_typ, ACTIVE_PREFIXES.get('new_tweet', ''))


try:
    import irclib
except ImportError:
    raise ImportError(
        "This module requires python irclib available from "
        + "https://github.com/sixohsix/python-irclib/zipball/python-irclib3-0.4.8")

OAUTH_FILE = os.environ.get('HOME', os.environ.get('USERPROFILE', '')) + os.sep + '.twitterbot_oauth'

def debug(msg):
    # uncomment this for debug text stuff
    # print(msg, file=sys.stdout)
    pass

class SchedTask(object):
    def __init__(self, task, delta):
        self.task = task
        self.delta = delta
        self.next = time.time()

    def __repr__(self):
        return "<SchedTask %s next:%i delta:%i>" %(
            self.task.__name__, self.__next__, self.delta)

    def __lt__(self, other):
        return self.next < other.next

    def __call__(self):
        return self.task()

class Scheduler(object):
    def __init__(self, tasks):
        self.task_heap = []
        for task in tasks:
            heappush(self.task_heap, task)

    def next_task(self):
        now = time.time()
        task = heappop(self.task_heap)
        wait = task.next - now
        task.next = now + task.delta
        heappush(self.task_heap, task)
        if (wait > 0):
            time.sleep(wait)
        task()
        #debug("tasks: " + str(self.task_heap))

    def run_forever(self):
        while True:
            self.next_task()


class TwitterBot(object):
    def __init__(self, configFilename):
        self.configFilename = configFilename
        self.config = load_config(self.configFilename)

        global ACTIVE_PREFIXES
        ACTIVE_PREFIXES = PREFIXES[self.config.get('irc', 'prefixes')]

        oauth_file = self.config.get('twitter', 'oauth_token_file')
        if not os.path.exists(oauth_file):
            oauth_dance("IRC Bot", CONSUMER_KEY, CONSUMER_SECRET, oauth_file)
        oauth_token, oauth_secret = read_token_file(oauth_file)

        self.twitter = Twitter(
            auth=OAuth(
                oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET),
            domain='api.twitter.com')

        self.irc = irclib.IRC()
        self.irc.add_global_handler('privmsg', self.handle_privmsg)
        self.irc.add_global_handler('ctcp', self.handle_ctcp)
        self.irc.add_global_handler('umode', self.handle_umode)
        self.ircServer = self.irc.server()

        self.sched = Scheduler(
            (SchedTask(self.process_events, 1),
             SchedTask(self.check_statuses, 120)))
        self.lastUpdate = (datetime.utcnow() - timedelta(minutes=10)).utctimetuple()

    def check_statuses(self):
        debug("In check_statuses")
        try:
            updates = reversed(self.twitter.statuses.home_timeline())
        except Exception as e:
            print("Exception while querying twitter:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return

        nextLastUpdate = self.lastUpdate
        for update in updates:
            crt = parsedate(update['created_at'])
            if (crt > nextLastUpdate):
                text = (htmlentitydecode(
                    update['text'].replace('\n', ' '))
                    .encode('utf8', 'replace'))

                # Skip updates beginning with @
                # TODO This would be better if we only ignored messages
                #   to people who are not on our following list.
                if not text.startswith(b"@"):
                    msg = "%s %s%s%s %s" %(
                        get_prefix(),
                        IRC_BOLD, update['user']['screen_name'],
                        IRC_BOLD, text.decode('utf8'))
                    self.privmsg_channels(msg)

                nextLastUpdate = crt

        self.lastUpdate = nextLastUpdate

    def process_events(self):
        self.irc.process_once()

    def handle_privmsg(self, conn, evt):
        debug('got privmsg')
        args = evt.arguments()[0].split(' ')
        try:
            if (not args):
                return
            if (args[0] == 'follow' and args[1:]):
                self.follow(conn, evt, args[1])
            elif (args[0] == 'unfollow' and args[1:]):
                self.unfollow(conn, evt, args[1])
            else:
                conn.privmsg(
                    evt.source().split('!')[0],
                    "%sHi! I'm Twitterbot! you can (follow "
                    "<twitter_name>) to make me follow a user or "
                    "(unfollow <twitter_name>) to make me stop." %
                    get_prefix())
        except Exception:
            traceback.print_exc(file=sys.stderr)

    def handle_ctcp(self, conn, evt):
        args = evt.arguments()
        source = evt.source().split('!')[0]
        if (args):
            if args[0] == 'VERSION':
                conn.ctcp_reply(source, "VERSION " + BOT_VERSION)
            elif args[0] == 'PING':
                conn.ctcp_reply(source, "PING")
            elif args[0] == 'CLIENTINFO':
                conn.ctcp_reply(source, "CLIENTINFO PING VERSION CLIENTINFO")

    def handle_umode(self, conn, evt):
        """
        QuakeNet ignores all your commands until after the MOTD. This
        handler defers joining until after it sees a magic line. It
        also tries to join right after connect, but this will just
        make it join again which should be safe.
        """
        args = evt.arguments()
        if (args and args[0] == '+i'):
            channels = self.config.get('irc', 'channel').split(',')
            for channel in channels:
                self.ircServer.join(channel)

    def privmsg_channels(self, msg):
        return_response=True
        channels=self.config.get('irc','channel').split(',')
        return self.ircServer.privmsg_many(channels, msg.encode('utf8'))

    def follow(self, conn, evt, name):
        userNick = evt.source().split('!')[0]
        friends = [x['name'] for x in self.twitter.statuses.friends()]
        debug("Current friends: %s" %(friends))
        if (name in friends):
            conn.privmsg(
                userNick,
                "%sI'm already following %s." %(get_prefix('error'), name))
        else:
            try:
                self.twitter.friendships.create(screen_name=name)
            except TwitterError:
                conn.privmsg(
                    userNick,
                    "%sI can't follow that user. Are you sure the name is correct?" %(
                        get_prefix('error')
                        ))
                return
            conn.privmsg(
                userNick,
                "%sOkay! I'm now following %s." %(get_prefix('followed'), name))
            self.privmsg_channels(
                "%s%s has asked me to start following %s" %(
                    get_prefix('inform'), userNick, name))

    def unfollow(self, conn, evt, name):
        userNick = evt.source().split('!')[0]
        friends = [x['name'] for x in self.twitter.statuses.friends()]
        debug("Current friends: %s" %(friends))
        if (name not in friends):
            conn.privmsg(
                userNick,
                "%sI'm not following %s." %(get_prefix('error'), name))
        else:
            self.twitter.friendships.destroy(screen_name=name)
            conn.privmsg(
                userNick,
                "%sOkay! I've stopped following %s." %(
                    get_prefix('stop_follow'), name))
            self.privmsg_channels(
                "%s%s has asked me to stop following %s" %(
                    get_prefix('inform'), userNick, name))

    def _irc_connect(self):
        self.ircServer.connect(
            self.config.get('irc', 'server'),
            self.config.getint('irc', 'port'),
            self.config.get('irc', 'nick'))
        channels=self.config.get('irc', 'channel').split(',')
        for channel in channels:
            self.ircServer.join(channel)

    def run(self):
        self._irc_connect()

        while True:
            try:
                self.sched.run_forever()
            except KeyboardInterrupt:
                break
            except TwitterError:
                # twitter.com is probably down because it
                # sucks. ignore the fault and keep going
                pass
            except irclib.ServerNotConnectedError:
                # Try and reconnect to IRC.
                self._irc_connect()


def load_config(filename):
    # Note: Python ConfigParser module has the worst interface in the
    # world. Mega gross.
    cp = ConfigParser()
    cp.add_section('irc')
    cp.set('irc', 'port', '6667')
    cp.set('irc', 'nick', 'twitterbot')
    cp.set('irc', 'prefixes', 'cats')
    cp.add_section('twitter')
    cp.set('twitter', 'oauth_token_file', OAUTH_FILE)

    cp.read((filename,))

    # attempt to read these properties-- they are required
    cp.get('twitter', 'oauth_token_file'),
    cp.get('irc', 'server')
    cp.getint('irc', 'port')
    cp.get('irc', 'nick')
    cp.get('irc', 'channel')

    return cp

# So there was a joke here about the twitter business model
# but I got rid of it. Not because I want this codebase to
# be "professional" in any way, but because someone forked
# this and deleted the comment because they couldn't take
# a joke. Hi guy!
#
# Fact: The number one use of Google Code is to look for that
# comment in the Linux kernel that goes "FUCK me gently with
# a chainsaw." Pretty sure Linus himself wrote it.

def main():
    configFilename = "twitterbot.ini"
    if (sys.argv[1:]):
        configFilename = sys.argv[1]

    try:
        if not os.path.exists(configFilename):
            raise Exception()
        load_config(configFilename)
    except Exception as e:
        print("Error while loading ini file %s" %(
            configFilename), file=sys.stderr)
        print(e, file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    bot = TwitterBot(configFilename)
    return bot.run()

########NEW FILE########
__FILENAME__ = logger
"""
twitter-log - Twitter Logger/Archiver

USAGE:

    twitter-log <screen_name> [max_id]

DESCRIPTION:

    Produce a complete archive in text form of a user's tweets. The
    archive format is:

        screen_name <tweet_id>
        Date: <tweet_time>
        [In-Reply-To: a_tweet_id]

            Tweet text possibly spanning multiple lines with
            each line indented by four spaces.


    Each tweet is separated by two blank lines.

"""

from __future__ import print_function

import sys
import os
from time import sleep

from .api import Twitter, TwitterError
from .cmdline import CONSUMER_KEY, CONSUMER_SECRET
from .auth import NoAuth
from .oauth import OAuth, write_token_file, read_token_file
from .oauth_dance import oauth_dance
from .util import printNicely

# Registered by @sixohsix
CONSUMER_KEY = "OifqLIQIufeY9znQCkbvg"
CONSUMER_SECRET = "IedFvi0JitR9yaYw9HwcCCEy4KYaLxf4p4rHRqGgX80"
OAUTH_FILENAME = os.environ.get('HOME', os.environ.get('USERPROFILE', '')) + os.sep + '.twitter_log_oauth'

def log_debug(msg):
    print(msg, file=sys.stderr)

def get_tweets(twitter, screen_name, max_id=None):
    kwargs = dict(count=3200, screen_name=screen_name)
    if max_id:
        kwargs['max_id'] = max_id

    n_tweets = 0
    tweets = twitter.statuses.user_timeline(**kwargs)
    for tweet in tweets:
        if tweet['id'] == max_id:
            continue
        print("%s %s\nDate: %s" % (tweet['user']['screen_name'],
                                   tweet['id'],
                                   tweet['created_at']))
        if tweet.get('in_reply_to_status_id'):
            print("In-Reply-To: %s" % tweet['in_reply_to_status_id'])
        print()
        for line in tweet['text'].splitlines():
            printNicely('    ' + line + '\n')
        print()
        print()
        max_id = tweet['id']
        n_tweets += 1
    return n_tweets, max_id

def main(args=sys.argv[1:]):
    if not args:
        print(__doc__)
        return 1

    if not os.path.exists(OAUTH_FILENAME):
        oauth_dance(
            "the Python Twitter Logger", CONSUMER_KEY, CONSUMER_SECRET,
            OAUTH_FILENAME)

    oauth_token, oauth_token_secret = read_token_file(OAUTH_FILENAME)

    twitter = Twitter(
        auth=OAuth(
            oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        domain='api.twitter.com')

    screen_name = args[0]

    if args[1:]:
        max_id = args[1]
    else:
        max_id = None

    n_tweets = 0
    while True:
        try:
            tweets_processed, max_id = get_tweets(twitter, screen_name, max_id)
            n_tweets += tweets_processed
            log_debug("Processed %i tweets (max_id %s)" %(n_tweets, max_id))
            if tweets_processed == 0:
                log_debug("That's it, we got all the tweets we could. Done.")
                break
        except TwitterError as e:
            log_debug("Twitter bailed out. I'm going to sleep a bit then try again")
            sleep(3)

    return 0

########NEW FILE########
__FILENAME__ = oauth
"""
Visit the Twitter developer page and create a new application:

    https://dev.twitter.com/apps/new

This will get you a CONSUMER_KEY and CONSUMER_SECRET.

When users run your application they have to authenticate your app
with their Twitter account. A few HTTP calls to twitter are required
to do this. Please see the twitter.oauth_dance module to see how this
is done. If you are making a command-line app, you can use the
oauth_dance() function directly.

Performing the "oauth dance" gets you an ouath token and oauth secret
that authenticate the user with Twitter. You should save these for
later so that the user doesn't have to do the oauth dance again.

read_token_file and write_token_file are utility methods to read and
write OAuth token and secret key values. The values are stored as
strings in the file. Not terribly exciting.

Finally, you can use the OAuth authenticator to connect to Twitter. In
code it all goes like this::

    MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
    if not os.path.exists(MY_TWITTER_CREDS):
        oauth_dance("My App Name", CONSUMER_KEY, CONSUMER_SECRET,
                    MY_TWITTER_CREDS)

    oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)

    twitter = Twitter(auth=OAuth(
        oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET))

    # Now work with Twitter
    twitter.statuses.update(status='Hello, world!')

"""

from __future__ import print_function

from time import time
from random import getrandbits

try:
    import urllib.parse as urllib_parse
    from urllib.parse import urlencode
    PY3 = True
except ImportError:
    import urllib2 as urllib_parse
    from urllib import urlencode
    PY3 = False

import hashlib
import hmac
import base64

from .auth import Auth


def write_token_file(filename, oauth_token, oauth_token_secret):
    """
    Write a token file to hold the oauth token and oauth token secret.
    """
    oauth_file = open(filename, 'w')
    print(oauth_token, file=oauth_file)
    print(oauth_token_secret, file=oauth_file)
    oauth_file.close()

def read_token_file(filename):
    """
    Read a token file and return the oauth token and oauth token secret.
    """
    f = open(filename)
    return f.readline().strip(), f.readline().strip()


class OAuth(Auth):
    """
    An OAuth authenticator.
    """
    def __init__(self, token, token_secret, consumer_key, consumer_secret):
        """
        Create the authenticator. If you are in the initial stages of
        the OAuth dance and don't yet have a token or token_secret,
        pass empty strings for these params.
        """
        self.token = token
        self.token_secret = token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def encode_params(self, base_url, method, params):
        params = params.copy()

        if self.token:
            params['oauth_token'] = self.token

        params['oauth_consumer_key'] = self.consumer_key
        params['oauth_signature_method'] = 'HMAC-SHA1'
        params['oauth_version'] = '1.0'
        params['oauth_timestamp'] = str(int(time()))
        params['oauth_nonce'] = str(getrandbits(64))

        enc_params = urlencode_noplus(sorted(params.items()))

        key = self.consumer_secret + "&" + urllib_parse.quote(self.token_secret, safe='~')

        message = '&'.join(
            urllib_parse.quote(i, safe='~') for i in [method.upper(), base_url, enc_params])

        signature = (base64.b64encode(hmac.new(
                    key.encode('ascii'), message.encode('ascii'), hashlib.sha1)
                                      .digest()))
        return enc_params + "&" + "oauth_signature=" + urllib_parse.quote(signature, safe='~')

    def generate_headers(self):
        return {}

# apparently contrary to the HTTP RFCs, spaces in arguments must be encoded as
# %20 rather than '+' when constructing an OAuth signature (and therefore
# also in the request itself.)
# So here is a specialized version which does exactly that.
# In Python2, since there is no safe option for urlencode, we force it by hand
def urlencode_noplus(query):
    if not PY3:
        new_query = []
        TILDE = '____TILDE-PYTHON-TWITTER____'
        for k,v in query:
            if type(k) is unicode: k = k.encode('utf-8')
            k = str(k).replace("~", TILDE)
            if type(v) is unicode: v = v.encode('utf-8')
            v = str(v).replace("~", TILDE)
            new_query.append((k, v))
        query = new_query
        return urlencode(query).replace(TILDE, "~").replace("+", "%20")

    return urlencode(query, safe='~').replace("+", "%20")

########NEW FILE########
__FILENAME__ = oauth2
"""
Visit the Twitter developer page and create a new application:

    https://dev.twitter.com/apps/new

This will get you a CONSUMER_KEY and CONSUMER_SECRET.

Twitter only supports the application-only flow of OAuth2 for certain
API endpoints. This OAuth2 authenticator only supports the application-only
flow right now. If twitter supports OAuth2 for other endpoints, this
authenticator may be modified as needed.

Finally, you can use the OAuth2 authenticator to connect to Twitter. In
code it all goes like this::

    twitter = Twitter(auth=OAuth2(bearer_token=BEARER_TOKEN))

    # Now work with Twitter
    twitter.search.tweets(q='keyword')

"""

from __future__ import print_function

try:
    from urllib.parse import quote, urlencode
except ImportError:
    from urllib import quote, urlencode

from base64 import b64encode
from .auth import Auth


class OAuth2(Auth):
    """
    An OAuth2 application-only authenticator.
    """
    def __init__(self, consumer_key=None, consumer_secret=None,
                 bearer_token=None):
        """
        Create an authenticator. You can supply consumer_key and
        consumer_secret if you are requesting a bearer_token. Otherwise
        you must supply the bearer_token.
        """
        self.bearer_token = None
        self.consumer_key = None
        self.consumer_secret = None

        if bearer_token:
            self.bearer_token = bearer_token
        elif consumer_key and consumer_secret:
            self.consumer_key = consumer_key
            self.consumer_secret = consumer_secret
        else:
            raise MissingCredentialsError(
                'You must supply either a bearer token, or both a '
                'consumer_key and a consumer_secret.')

    def encode_params(self, base_url, method, params):

        return urlencode(params)

    def generate_headers(self):
        if self.bearer_token:
            headers = {
                b'Authorization': 'Bearer {0}'.format(
                    self.bearer_token).encode('utf8')
            }

        elif self.consumer_key and self.consumer_secret:

            headers = {
                b'Content-Type': (b'application/x-www-form-urlencoded;'
                                  b'charset=UTF-8'),
                b'Authorization': 'Basic {0}'.format(
                    b64encode('{0}:{1}'.format(
                        quote(self.consumer_key),
                        quote(self.consumer_secret)).encode('utf8')
                    ).decode('utf8')
                ).encode('utf8')
            }

        else:
            raise MissingCredentialsError(
                'You must supply either a bearer token, or both a '
                'consumer_key and a consumer_secret.')

        return headers


class MissingCredentialsError(Exception):
    pass

########NEW FILE########
__FILENAME__ = oauth_dance
from __future__ import print_function

import webbrowser
import time

from .api import Twitter
from .oauth import OAuth, write_token_file

try:
    _input = raw_input
except NameError:
    _input = input



def oauth_dance(app_name, consumer_key, consumer_secret, token_filename=None):
    """
    Perform the OAuth dance with some command-line prompts. Return the
    oauth_token and oauth_token_secret.

    Provide the name of your app in `app_name`, your consumer_key, and
    consumer_secret. This function will open a web browser to let the
    user allow your app to access their Twitter account. PIN
    authentication is used.

    If a token_filename is given, the oauth tokens will be written to
    the file.
    """
    print("Hi there! We're gonna get you all set up to use %s." % app_name)
    twitter = Twitter(
        auth=OAuth('', '', consumer_key, consumer_secret),
        format='', api_version=None)
    oauth_token, oauth_token_secret = parse_oauth_tokens(
        twitter.oauth.request_token())
    print("""
In the web browser window that opens please choose to Allow
access. Copy the PIN number that appears on the next page and paste or
type it here:
""")
    oauth_url = ('https://api.twitter.com/oauth/authorize?oauth_token=' +
                 oauth_token)
    print("Opening: %s\n" % oauth_url)
    return oauth_url, oauth_token, oauth_token_secret

##################################################################################################################

    try:
        r = webbrowser.open(oauth_url)
        time.sleep(2) # Sometimes the last command can print some
                      # crap. Wait a bit so it doesn't mess up the next
                      # prompt.
        if not r:
            raise Exception()
    except:
        print("""
Uh, I couldn't open a browser on your computer. Please go here to get
your PIN:

""" + oauth_url)
    oauth_verifier = _input("Please enter the PIN: ").strip()
    twitter = Twitter(
        auth=OAuth(
            oauth_token, oauth_token_secret, consumer_key, consumer_secret),
        format='', api_version=None)
    oauth_token, oauth_token_secret = parse_oauth_tokens(
        twitter.oauth.access_token(oauth_verifier=oauth_verifier))
    if token_filename:
        write_token_file(
            token_filename, oauth_token, oauth_token_secret)
        print()
        print("That's it! Your authorization keys have been written to %s." % (
            token_filename))
    return oauth_token, oauth_token_secret

def oauth_dance_verify(consumer_key, consumer_secret, oauth_token, oauth_token_secret, pin, token_filename=None):
    
    oauth_verifier = str(pin).strip()
    twitter = Twitter(
        auth=OAuth(
            oauth_token, oauth_token_secret, consumer_key, consumer_secret),
        format='', api_version=None)
    oauth_token, oauth_token_secret = parse_oauth_tokens(
        twitter.oauth.access_token(oauth_verifier=oauth_verifier))
    if token_filename:
        write_token_file(
            token_filename, oauth_token, oauth_token_secret)
        print()
        print("That's it! Your authorization keys have been written to %s." % (
            token_filename))
    return oauth_token, oauth_token_secret


def parse_oauth_tokens(result):
    for r in result.split('&'):
        k, v = r.split('=')
        if k == 'oauth_token':
            oauth_token = v
        elif k == 'oauth_token_secret':
            oauth_token_secret = v
    return oauth_token, oauth_token_secret

########NEW FILE########
__FILENAME__ = stream
try:
    import urllib.request as urllib_request
    import urllib.error as urllib_error
    import io
except ImportError:
    import urllib2 as urllib_request
    import urllib2 as urllib_error
import json
from ssl import SSLError
import socket
import sys, select, time

from .api import TwitterCall, wrap_response, TwitterHTTPError

def recv_chunk(sock):  # -> bytearray:

    buf = sock.recv(8)  # Scan for an up to 16MiB chunk size (0xffffff).
    crlf = buf.find(b'\r\n')  # Find the HTTP chunk size.

    if crlf > 0:  # If there is a length, then process it

        remaining = int(buf[:crlf], 16)  # Decode the chunk size.

        start = crlf + 2  # Add in the length of the header's CRLF pair.
        end = len(buf) - start

        chunk = bytearray(remaining)

        if remaining <= 2:  # E.g. an HTTP chunk with just a keep-alive delimiter or end of stream (0).
            chunk[:remaining] = buf[start:start + remaining]
        # There are several edge cases (remaining == [3-6]) as the chunk size exceeds the length
        # of the initial read of 8 bytes. With Twitter, these do not, in practice, occur. The
        # shortest JSON message starts with '{"limit":{'. Hence, it exceeds in size the edge cases
        # and eliminates the need to address them.
        else:  # There is more to read in the chunk.
            chunk[:end] = buf[start:]
            chunk[end:] = sock.recv(remaining - end)
            sock.recv(2)  # Read the trailing CRLF pair. Throw it away.

        return chunk

    return bytearray()

##  recv_chunk()


class TwitterJSONIter(object):

    def __init__(self, handle, uri, arg_data, block=True, timeout=None):
        self.handle = handle
        self.uri = uri
        self.arg_data = arg_data
        self.block = block
        self.timeout = timeout


    def __iter__(self):
        sock = self.handle.fp.raw._sock if sys.version_info >= (3, 0) else self.handle.fp._sock.fp._sock
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setblocking(self.block and not self.timeout)
        buf = ''
        json_decoder = json.JSONDecoder()
        timer = time.time()
        while True:
            try:
                buf = buf.lstrip()
                res, ptr = json_decoder.raw_decode(buf)
                buf = buf[ptr:]
                yield wrap_response(res, self.handle.headers)
                timer = time.time()
                continue
            except ValueError as e:
                if self.block: pass
                else: yield None
            try:
                buf = buf.lstrip()  # Remove any keep-alive delimiters to detect hangups.
                if self.timeout:
                    ready_to_read = select.select([sock], [], [], self.timeout)
                    if ready_to_read[0]:
                        buf += recv_chunk(sock).decode('utf-8')  # This is a non-blocking read.
                        if time.time() - timer > self.timeout:
                            yield {'timeout': True}
                    else: yield {'timeout': True}
                else:
                    buf += recv_chunk(sock).decode('utf-8')
                if not buf and self.block:
                    yield {'hangup': True}
                    break
            except SSLError as e:
                # Error from a non-blocking read of an empty buffer.
                if (not self.block or self.timeout) and (e.errno == 2): pass
                else: raise

def handle_stream_response(req, uri, arg_data, block, timeout=None):
    try:
        handle = urllib_request.urlopen(req,)
    except urllib_error.HTTPError as e:
        raise TwitterHTTPError(e, uri, 'json', arg_data)
    return iter(TwitterJSONIter(handle, uri, arg_data, block, timeout=timeout))

class TwitterStreamCallWithTimeout(TwitterCall):
    def _handle_response(self, req, uri, arg_data, _timeout=None):
        return handle_stream_response(req, uri, arg_data, block=True, timeout=self.timeout)

class TwitterStreamCall(TwitterCall):
    def _handle_response(self, req, uri, arg_data, _timeout=None):
        return handle_stream_response(req, uri, arg_data, block=True)

class TwitterStreamCallNonBlocking(TwitterCall):
    def _handle_response(self, req, uri, arg_data, _timeout=None):
        return handle_stream_response(req, uri, arg_data, block=False)

class TwitterStream(TwitterStreamCall):
    """
    The TwitterStream object is an interface to the Twitter Stream API
    (stream.twitter.com). This can be used pretty much the same as the
    Twitter class except the result of calling a method will be an
    iterator that yields objects decoded from the stream. For
    example::

        twitter_stream = TwitterStream(auth=OAuth(...))
        iterator = twitter_stream.statuses.sample()

        for tweet in iterator:
            ...do something with this tweet...

    The iterator will yield tweets forever and ever (until the stream
    breaks at which point it raises a TwitterHTTPError.)

    The `block` parameter controls if the stream is blocking. Default
    is blocking (True). When set to False, the iterator will
    occasionally yield None when there is no available message.
    """
    def __init__(
        self, domain="stream.twitter.com", secure=True, auth=None,
        api_version='1.1', block=True, timeout=None):
        uriparts = ()
        uriparts += (str(api_version),)

        if block:
            if timeout:
                call_cls = TwitterStreamCallWithTimeout
            else:
                call_cls = TwitterStreamCall
        else:
            call_cls = TwitterStreamCallNonBlocking

        TwitterStreamCall.__init__(
            self, auth=auth, format="json", domain=domain,
            callable_cls=call_cls,
            secure=secure, uriparts=uriparts, timeout=timeout, gzip=False)

########NEW FILE########
__FILENAME__ = stream_example
"""
Example program for the Stream API. This prints public status messages
from the "sample" stream as fast as possible.

USAGE

  stream-example -t <token> -ts <token_secret> -ck <consumer_key> -cs <consumer_secret>

"""

from __future__ import print_function

import argparse

from twitter.stream import TwitterStream
from twitter.oauth import OAuth
from twitter.util import printNicely


def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument('-t',  '--token', help='The Twitter Access Token.')
    parser.add_argument('-ts', '--token_secret', help='The Twitter Access Token Secret.')
    parser.add_argument('-ck', '--consumer_key', help='The Twitter Consumer Key.')
    parser.add_argument('-cs', '--consumer_secret', help='The Twitter Consumer Secret.')
    parser.add_argument('-us', '--user_stream', action='store_true', help='Connect to the user stream endpoint.')
    parser.add_argument('-ss', '--site_stream', action='store_true', help='Connect to the site stream endpoint.')

    return parser.parse_args()

def main():
    args = parse_arguments()

    if not all((args.token, args.token_secret, args.consumer_key, args.consumer_secret)):
        print(__doc__)
        return 2

    # When using twitter stream you must authorize.
    auth = OAuth(args.token, args.token_secret, args.consumer_key, args.consumer_secret)
    if args.user_stream:
        stream = TwitterStream(auth=auth, domain='userstream.twitter.com')
        tweet_iter = stream.user()
    elif args.site_stream:
        stream = TwitterStream(auth=auth, domain='sitestream.twitter.com')
        tweet_iter = stream.site()
    else:
        stream = TwitterStream(auth=auth, timeout=60.0)
        tweet_iter = stream.statuses.sample()

    # Iterate over the sample stream.
    for tweet in tweet_iter:
        # You must test that your tweet has text. It might be a delete
        # or data message.
        if tweet.get('text'):
            printNicely(tweet['text'])

if __name__ == '__main__':
    main()

########NEW FILE########
__FILENAME__ = timezones
# Retrieved from http://docs.python.org/2/library/datetime.html on 2013-05-24
from datetime import tzinfo, timedelta, datetime

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

# A UTC class.

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = UTC()

# A class building tzinfo objects for fixed-offset time zones.
# Note that FixedOffset(0, "UTC") is a different way to build a
# UTC tzinfo object.

class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = timedelta(minutes = offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

# A class capturing the platform's idea of local time.

import time as _time

STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

Local = LocalTimezone()


########NEW FILE########
__FILENAME__ = twitter_globals
'''
    This module is automatically generated using `update.py`

    .. data:: POST_ACTIONS
        List of twitter method names that require the use of POST
'''

POST_ACTIONS = [

    # Status Methods
    'update', 'retweet', 'update_with_media',

    # Direct Message Methods
    'new',

    # Account Methods
    'update_profile_image', 'update_delivery_device', 'update_profile',
    'update_profile_background_image', 'update_profile_colors',
    'update_location', 'end_session', 'settings',
    'update_profile_banner', 'remove_profile_banner',

    # Notification Methods
    'leave', 'follow',

    # Status Methods, Block Methods, Direct Message Methods,
    # Friendship Methods, Favorite Methods
    'destroy', 'destroy_all',

    # Block Methods, Friendship Methods, Favorite Methods
    'create', 'create_all',

    # Users Methods
    'lookup', 'report_spam',

    # Streaming Methods
    'filter', 'user', 'site',

    # OAuth Methods
    'token', 'access_token',
    'request_token', 'invalidate_token',
]

########NEW FILE########
__FILENAME__ = util
"""
Internal utility functions.

`htmlentitydecode` came from here:
    http://wiki.python.org/moin/EscapingHtml
"""

from __future__ import print_function

import contextlib
import re
import sys
import time

try:
    from html.entities import name2codepoint
    unichr = chr
    import urllib.request as urllib2
    import urllib.parse as urlparse
except ImportError:
    from htmlentitydefs import name2codepoint
    import urllib2
    import urlparse

def htmlentitydecode(s):
    return re.sub(
        '&(%s);' % '|'.join(name2codepoint),
        lambda m: unichr(name2codepoint[m.group(1)]), s)

def smrt_input(globals_, locals_, ps1=">>> ", ps2="... "):
    inputs = []
    while True:
        if inputs:
            prompt = ps2
        else:
            prompt = ps1
        inputs.append(input(prompt))
        try:
            ret = eval('\n'.join(inputs), globals_, locals_)
            if ret:
                print(str(ret))
            return
        except SyntaxError:
            pass

def printNicely(string):
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout.buffer.write(string.encode('utf8'))
        print()
    else:
        print(string.encode('utf8'))

__all__ = ["htmlentitydecode", "smrt_input"]

def err(msg=""):
    print(msg, file=sys.stderr)

class Fail(object):
    """A class to count fails during a repetitive task.

    Args:
        maximum: An integer for the maximum of fails to allow.
        exit: An integer for the exit code when maximum of fail is reached.

    Methods:
        count: Count a fail, exit when maximum of fails is reached.
        wait: Same as count but also sleep for a given time in seconds.
    """
    def __init__(self, maximum=10, exit=1):
        self.i = maximum
        self.exit = exit

    def count(self):
        self.i -= 1
        if self.i == 0:
            err("Too many consecutive fails, exiting.")
            raise SystemExit(self.exit)

    def wait(self, delay=0):
        self.count()
        if delay > 0:
            time.sleep(delay)


def find_links(line):
    """Find all links in the given line. The function returns a sprintf style
    format string (with %s placeholders for the links) and a list of urls."""
    l = line.replace("%", "%%")
    regex = "(https?://[^ )]+)"
    return (
        re.sub(regex, "%s", l),
        [m.group(1) for m in re.finditer(regex, l)])

def follow_redirects(link, sites= None):
    """Follow directs for the link as long as the redirects are on the given
    sites and return the resolved link."""
    def follow(url):
        return sites == None or urlparse.urlparse(url).hostname in sites

    class RedirectHandler(urllib2.HTTPRedirectHandler):
        def __init__(self):
            self.last_url = None
        def redirect_request(self, req, fp, code, msg, hdrs, newurl):
            self.last_url = newurl
            if not follow(newurl):
                return None
            r = urllib2.HTTPRedirectHandler.redirect_request(
                self, req, fp, code, msg, hdrs, newurl)
            r.get_method = lambda : 'HEAD'
            return r

    if not follow(link):
        return link
    redirect_handler = RedirectHandler()
    opener = urllib2.build_opener(redirect_handler)
    req = urllib2.Request(link)
    req.get_method = lambda : 'HEAD'
    try:
        with contextlib.closing(opener.open(req)) as site:
            return site.url
    except (urllib2.HTTPError, urllib2.URLError):
        return redirect_handler.last_url if redirect_handler.last_url else link

def expand_line(line, sites):
    """Expand the links in the line for the given sites."""
    l = line.strip()
    msg_format, links = find_links(l)
    args = tuple(follow_redirects(l, sites) for l in links)
    return msg_format % args

def parse_host_list(list_of_hosts):
    """Parse the comma separated list of hosts."""
    p = set(
        m.group(1) for m in re.finditer("\s*([^,\s]+)\s*,?\s*", list_of_hosts))
    return p


########NEW FILE########
__FILENAME__ = SublimeTweet
# coding=utf-8
#author: Rozboris (rozboris.com)
#version: 0.9
import sublime
import sublime_plugin
import json
import threading
import os
import urllib.request as req
from datetime import datetime
from .libs.twitter import *
from .libs.reltime import *
import webbrowser

consumer_key = '8m6wYJ3w8J7PxaZxTMkzw'
consumer_secret = 'XnbfrGRC0n93b37PaN7tZa53RuNbExeHRV1gToh4'
url_that_always_online = 'http://twitter.com'
timeout = 2
tweetsCount = 40


class ReadTweetsCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.internetStatus = None
    self.settingsController = SublimeTweetSettingsController()
    sublime.status_message('Checking your internet connection...')
    threading.Thread(target=checkInternetConnection, args=(self.setInternetStatus, timeout, self.settingsController)).start()

  def setInternetStatus(self, status):
    self.internetStatus = status
    if not self.internetStatus:
      print('No internet connection, sorry!')
      sublime.error_message('Sublime Tweet: Please check your internet connection! It looks like it is down (or just twitter.com is down).')
      return
    else:
      sublime.set_timeout(self.prepareTweetsFromTimeline, 0)

  def prepareTweetsFromTimeline(self):
    sublime.status_message('')
    if not self.settingsController.checkIfEverythingIsReady():
      TwitterUserRegistration(self.window).register(self.run)
      return

    self.api = Twitter(auth=OAuth(
      self.settingsController.s['twitter_access_token_key'],
      self.settingsController.s['twitter_access_token_secret'],
      consumer_key,
      consumer_secret,
    ))
    sublime.status_message('Loading tweets from timeline...')
    threading.Thread(target=self.loadTweetsFromTimelineInBackground).start()

  def loadTweetsFromTimelineInBackground(self):
    try:
      self.tweets = self.api.statuses.home_timeline(count = tweetsCount, include_entities = True)
      sublime.set_timeout(self.onTweetsFromTimelineLoaded, 0)
    except TwitterError as e:
      sublime.status_message('We encountered an error: ' + str(e))
      self.settingsController.s['twitter_has_token'] = False
      self.settingsController.saveSettings()
      TwitterUserRegistration(self.window).register(self.run)
      return
    except Exception as e:
      print('We have some connection issues', e)
      self.tweets = None

  def onTweetsFromTimelineLoaded(self):
    if self.tweets:
      previouslyShownTweets = self.settingsController.s.get('previously_shown_tweets', None)
      self.settingsController.s['previously_shown_tweets'] = [s['id'] for s in self.tweets]
      self.settingsController.saveSettings()
      for t in self.tweets:
        t['new'] = False
        if not previouslyShownTweets or not len(previouslyShownTweets) or t['id'] not in previouslyShownTweets:
          t['new'] = True

      sublime.set_timeout(self.showTweetsOnPanel, 0)

  def showTweetsOnPanel(self):
    self.tweet_texts = []
    if self.tweets and len(self.tweets) > 0:
      for s in self.tweets:
        firstLine  = s['text']
        created_at = datetime.strptime(s['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        created_at_relative = reltime(created_at)
        secondLine = '@%s (%s)' % (s['user']['screen_name'], created_at_relative)
        if 'new' in s and s['new']: 
          secondLine = '☀ ' + secondLine
        if 'favorited' in s and s['favorited']:
          secondLine = '★ ' + secondLine
        if 'retweeted' in s and s['retweeted']:
          secondLine = '↺ ' + secondLine

        self.tweet_texts.append([firstLine, secondLine])
    else:
      self.tweet_texts.append(['No tweets to show', 'If you think it\'s an error - please contact an author'])
    self.showTweets()

  def showTweets(self, number = None):
    sublime.set_timeout(lambda: self.window.show_quick_panel(self.tweet_texts, self.onTweetSelected), 10)

  def onTweetSelected(self, number):
    if number > -1 and self.tweets and len(self.tweets) > 0:
      self.selectedTweet = self.tweets[number]
      sublime.status_message(self.selectedTweet['text'])
      self.currentTweetActions = list([
        [['← Back', ''], ReadTweetsCommand.showTweets],
      ])
      if self.selectedTweet['favorited']:
        self.currentTweetActions.append([['★ Remove Favorite', ''], ReadTweetsCommand.doUnFavorite])
      else:
        self.currentTweetActions.append([['★ Favorite', ''], ReadTweetsCommand.doFavorite])

      if not self.selectedTweet['retweeted']:
        self.currentTweetActions.append([['↺ Retweet', ''], ReadTweetsCommand.doRetweet])

      self.currentTweetActions.append([['@ Reply', ''], ReadTweetsCommand.doReply])

      if 'urls' in self.selectedTweet['entities']:
        for url in self.selectedTweet['entities']['urls']:
          self.currentTweetActions.append([[url['expanded_url'], 'Open URL in external browser'], None])
      if 'media' in self.selectedTweet['entities']:
        for m in self.selectedTweet['entities']['media']:
          self.currentTweetActions.append([[m['expanded_url'], 'Open image in external browser'], None])
      actionPresentation = [strings for strings, function in self.currentTweetActions]
      sublime.set_timeout(lambda: self.window.show_quick_panel(actionPresentation, self.onTweetActionSelected), 10)

  def onTweetActionSelected(self, number):
    if number < 0:
      return
    try:
      [presentation, func] = self.currentTweetActions[number]
      if func:
        func(self, self.selectedTweet)
      else:
        url = presentation[0]
        webbrowser.open(url)
    except Exception as error:
      self.handleError(error)

  def doReply(self, tweet):
    self.window.run_command('tweet', {
      'replyToName': tweet['user']['screen_name'],
      'replyToId': tweet['id']
    })

  def doRetweet(self, tweet):
    print(tweet)
    try:
      self.api.statuses.retweet(id = tweet['id'])
      sublime.status_message('Tweet was retweeted')
      tweet['retweeted'] = True
      self.showTweetsOnPanel()
    except TwitterError as e:
      sublime.status_message('We encountered an error: ' + str(e))
      self.settingsController.s['twitter_has_token'] = False
      self.settingsController.saveSettings()
      TwitterUserRegistration(self.window).register(self.run)
      return
    except Exception as error:
      self.handleError(error)

  def doFavorite(self, tweet):
    try:
      self.api.favorites.create(_id = tweet['id'])
      sublime.status_message('Tweet was favorited')
      tweet['favorited'] = True
      self.showTweetsOnPanel()
    except TwitterError as e:
      sublime.status_message('We encountered an error: ' + str(e))
      self.settingsController.s['twitter_has_token'] = False
      self.settingsController.saveSettings()
      TwitterUserRegistration(self.window).register(self.run)
      return
    except Exception as error:
      self.handleError(error)

  def doUnFavorite(self, tweet):
    try:
      self.api.favorites.destroy(_id = tweet['id'])
      sublime.status_message('Tweet was UNFavorited')
      tweet['favorited'] = False
      self.showTweetsOnPanel()
    except TwitterError as e:
      sublime.status_message('We encountered an error: ' + str(e))
      self.settingsController.s['twitter_has_token'] = False
      self.settingsController.saveSettings()
      TwitterUserRegistration(self.window).register(self.run)
      return
    except Exception as error:
      self.handleError(error)

  def handleError(self, error):
    print('handleError: ', error)
    sublime.status_message('Sorry, we have some problems. Please, try again.')
    self.settingsController.s['twitter_has_token'] = False
    self.settingsController.saveSettings()
    TwitterUserRegistration(self.window).register(self.run)
    return


class TweetCommand(sublime_plugin.WindowCommand):
  def run(self, replyToName=None, replyToId=None):
    self.maxlength = 140
    self.replyToId = replyToId
    if replyToId:
      self.prefix = '@%s ' % replyToName
    else:
      self.prefix = ''
    self.internetStatus = None
    self.settingsController = SublimeTweetSettingsController()
    sublime.status_message('Checking your internet connection...')
    threading.Thread(target = checkInternetConnection, args = (self.setInternetStatus, timeout, self.settingsController)).start()

  def setInternetStatus(self, status):
    self.internetStatus = status
    sublime.set_timeout(self.runIfInternetIsUp, 0)

  def runIfInternetIsUp(self):
    if not self.internetStatus:
      print('No internet connection, sorry!')
      sublime.status_message('Please check your internet connection!')
      return

    sublime.status_message('')

    if not self.settingsController.checkIfEverythingIsReady():
      TwitterUserRegistration(self.window).register(self.run)
      return

    if self.replyToId:
      message = 'Reply to %s:' % self.prefix.strip()
    else:
      message = 'Tweet:'
    self.window.show_input_panel(message, '', self.on_entered_tweet, self.update_character_counter_on_entering_tweet, None)

  def update_character_counter_on_entering_tweet(self, text):
    remaining = self.maxlength - len(self.prefix + text)
    if remaining >= 0:
      m = 'Charaters remain: %d' % remaining
    else:
      m = '★ ★ ★ YOUR MESSAGE IS %d CHARACTERS LONG! ★ ★ ★ ' % (-remaining, )
    sublime.status_message(m)

  def on_entered_tweet(self, text):
    if not len(text):
      return
    sublime.status_message('Sending tweet...')
    text = self.prefix + text
    api = Twitter(auth=OAuth(
      self.settingsController.s['twitter_access_token_key'], 
      self.settingsController.s['twitter_access_token_secret'], 
      consumer_key, 
      consumer_secret))
    if len(text) > self.maxlength:
      after = '... cont.'
      text = text[:self.maxlength - len(after)] + after
      sublime.message_dialog('Your tweet is longer than %d symbols, so it was truncated to %d and posted anyway.' % (self.maxlength, ))
    text = text.encode('utf8')
    try:
      if self.replyToId:
        api.statuses.update(status = text, in_reply_to_status_id = self.replyToId)
      else:
        api.statuses.update(status = text)
    except TwitterError as e:
      sublime.status_message('We encountered an error: ' + str(e))
      self.settingsController.s['twitter_has_token'] = False
      self.settingsController.saveSettings()
      TwitterUserRegistration(self.window).register(self.run)
      return
    except Exception as e:
      sublime.status_message('Sorry, we have some problems. Please, try again.')
      self.settingsController.s['twitter_has_token'] = False
      self.settingsController.saveSettings()
      TwitterUserRegistration(self.window).register(self.run)
      return
    sublime.status_message('Your tweet was posted!')
    print('Tweet was posted!')


class SublimeTweetSettingsController:
  def __init__(self, filename='SublimeTweet.settings'):
    self.settingsThatShouldBeTrue = ['twitter_has_token', 'twitter_access_token_key', 'twitter_access_token_secret']
    self.defaultSettings = {
      'previously_shown_tweets': []
    }
    for setting in self.settingsThatShouldBeTrue:
      self.defaultSettings[setting] = False

    self.filename = os.path.join(sublime.packages_path(), 'User', filename)
    self.s = self.loadSettings()

  def loadSettings(self):
    try:
      contents = open(self.filename).read()
      decoded = json.loads(contents)
      if 'twitter_have_token' in decoded:
        decoded['twitter_has_token'] = decoded['twitter_have_token']
        del decoded['twitter_have_token']
      return decoded
    except:
      self.s = self.defaultSettings
      self.saveSettings()
      return self.s

  def saveSettings(self):
    try:
      with open(self.filename, 'w') as f:
        f.write(json.dumps(self.s, sort_keys=True, indent=2))
    except Exception as e:
      print(e.message)
      sublime.error_message('Sublime Tweet: Can\'t save settings and can\'t fix it either, sorry :(')
      pass  # TODO

  def checkIfEverythingIsReady(self):
    everythingsgood = True
    for setting in self.settingsThatShouldBeTrue:
      if setting not in self.s or not self.s[setting]:
        everythingsgood = False
    return everythingsgood


def checkInternetConnection(callback, timeout, settings):
  try:
    req.urlopen(url_that_always_online, timeout=timeout)
    settings.saveSettings()
    callback(True)
  except:
    callback(False)

class TwitterUserRegistration(sublime_plugin.WindowCommand):
  def __init__(self, window):
    self.window = window
    self.action_when_done = None

  def register(self, action_when_done = None):
    self.settingsController = SublimeTweetSettingsController()
    self.oauth_token = ''
    self.oauth_token_secret = ''
    self.action_when_done = action_when_done

    if not self.settingsController.checkIfEverythingIsReady():
      try:
        ready = sublime.ok_cancel_dialog(
'You are starting Sublime Tweet for the first time, \
please authorize it to use your account. Now I will open your default browser. \n\n\
Please log in, click "Authorize" and then copy a PIN code. Then go back to Sublime Text and enter PIN at the bottom of your screen.\n\
You should only do it once.\n\nAre you ready?', 'I am ready!'
        )
        if not ready:
          return

        (url, self.oauth_token, self.oauth_token_secret) = oauth_dance("Sublime Tweet", consumer_key, consumer_secret)
      except e:
        sublime.error_message('Problems with the first step. Try again.\n')
        print('Exception: ', e)
        sublime.status_message('Please, try calling me again. We have some problems with auth')
        return

      if url:
        message = 'I\'ve opened a browser for you. Please authorize me and enter the pin:'
        self.window.show_input_panel(message, '', self.on_entered_pin, None, None)
        webbrowser.open(url)
      else:
        print('Please try again later')

  def on_entered_pin(self, text):
    try:
      pin = str(text)
      keys = oauth_dance_verify(consumer_key, consumer_secret, self.oauth_token, self.oauth_token_secret, pin)
    except ValueError:
      sublime.error_message('We have some problems with pin. Please, try again.')
      self.register()
      return
    except e:
      sublime.error_message('We have some problems with the second auth step. Please, try again. ', e)
      self.register()
      sublime.status_message('We have some problems with the second auth step. Please, try again.')
      return

    self.access_token_key, self.access_token_secret = keys
    sublime.status_message('You are authorized me, thanks! Now you can tweet from Sublime Text 2.')
    self.settingsController.s['twitter_has_token'] = True
    self.settingsController.s['twitter_access_token_key'] = self.access_token_key
    self.settingsController.s['twitter_access_token_secret'] = self.access_token_secret
    self.settingsController.saveSettings()
    if self.action_when_done:
      self.action_when_done()
########NEW FILE########
