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

    def twit(self, irc, msg, args, opts, query):
        """
        @twit [--from user][query]

        Return the last three tweets matching a given string 
        and/or user. if no query specified returns a random tweet from 
        the public timeline if no
        """

        screen_name = None
        for (opt, arg) in opts:
            if opt == 'from':
                screen_name = arg

        def fetch_json(url):
            json = web.getUrl(url, headers=HEADERS)
            try:
                response = simplejson.loads(json)
            except ValueError:
                reponse = None
            return response
            
        resp = 'Gettin nothin from teh twitter.'
        if query:
            if screen_name:
                query = "from:%s %s" % (screen_name, query)
            url = 'http://search.twitter.com/search.json?' 
            tweets = fetch_json(url + urlencode({ 'q': query, 'rpp': 3 }))['results']
            if tweets:
                extracted = ["%s: %s" % (x['from_user'], x['text']) for x in tweets]
                resp = ' ;; '.join(extracted)
        else:
            if screen_name:
                url = 'http://twitter.com/statuses/user_timeline.json?'
                url = url + urlencode({'screen_name': screen_name})
            else:
                url = 'http://twitter.com/statuses/public_timeline.json?'
            tweets = fetch_json(url)
            if tweets:
                tweet = tweets[0] #randint(0, len(tweets)-1)]
                resp = "%s: %s" % (tweet['user']['screen_name'], tweet['text'])
        irc.reply(resp.encode('utf8','ignore'))

    twit = wrap(twit, [getopts({'from':'something'}), optional('text')])

Class = Twitter


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
