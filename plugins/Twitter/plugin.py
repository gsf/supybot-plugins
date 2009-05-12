###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from random import randint
import simplejson
import supybot.utils.web as web
from urllib import urlencode

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; DBPedia Plugin; http://code4lib.org/irc)')

class Twitter(callbacks.Plugin):
    """Add the help for "@plugin help Twitter" here
    This should describe *how* to use this plugin."""
    threaded = True

    def twit(self, irc, msg, args, query):
        """
        @twit [query]

        Return the last three tweets matching a given string,
        if no query specified returns a random tweet from 
        the public timeline if no
        """

        def fetch_json(url):
            json = web.getUrl(url, headers=HEADERS)
            return simplejson.loads(json)
            
        if query:
            url = 'http://search.twitter.com/search.json?' 
            tweets = fetch_json(url + urlencode({ 'q': query, 'rpp': 3 }))['results']
            extracted = ["%s: %s" % (x['from_user'], x['text']) for x in tweets]
            resp = ' ;; '.join(extracted)
        else:
            url = 'http://twitter.com/statuses/public_timeline.json?'
            tweets = fetch_json(url)
            tweet = tweets[randint(0, len(tweets)-1)]
            resp = "%s: %s" % (tweet['user']['screen_name'], tweet['text'])

        irc.reply(resp.encode('utf8','ignore'))

    twit = wrap(twit, [optional('text')])
    tweet = wrap(twit, [optional('text')])

Class = Twitter


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
