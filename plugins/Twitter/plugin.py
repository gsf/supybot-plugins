
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from random import randint
import simplejson
import supybot.utils.web as web
from urllib import urlencode
from BeautifulSoup import BeautifulStoneSoup as BSS

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; DBPedia Plugin; http://code4lib.org/irc)')

class Twitter(callbacks.Plugin):
    """Add the help for "@plugin help Twitter" here
    This should describe *how* to use this plugin."""
    threaded = True

    def trends(self, irc, msg, args, timeframe):
        """@trends [current|daily|weekly]

        Return top trending Twitter topics for one of three timeframes:
        current, daily or weekly. Default is current.
        """

        if not timeframe:
            timeframe = 'current'
        if timeframe not in ['current', 'daily', 'weekly']:
            irc.reply("Invalid timeframe. Must be one of 'current', 'daily' or 'weekly'")
            return

        url = 'http://search.twitter.com/trends/%s.json' % timeframe
        try:
            doc = web.getUrl(url, headers=HEADERS)
            json = simplejson.loads(doc)
        except: 
            irc.reply("uh-oh, something went awry")
            return

        trends = json['trends'].values()[0]
        tnames = [x['name'] for x in trends]
        resp = ', '.join(["%d. %s" % t for t in zip(range(1, len(tnames) + 1), tnames)])
        irc.reply(resp.encode('utf8','ignore'))

    trends = wrap(trends, [optional('text')])

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
            doc = web.getUrl(url, headers=HEADERS)
            try:
                json = simplejson.loads(doc)
            except ValueError:
                return None
            return json
            
        resp = 'Gettin nothin from teh twitter.'
        if query:
            if screen_name:
                query = "from:%s %s" % (screen_name, query)
            url = 'http://search.twitter.com/search.json?' 
            json = fetch_json(url + urlencode({ 'q': query, 'rpp': 3 }))
            try:
                tweets = json['results']
                extracted = ["%s: %s" % (x['from_user'], x['text']) for x in tweets]
                resp = ' ;; '.join(extracted)
            except:
                pass
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
        resp = BSS(resp, convertEntities=BSS.HTML_ENTITIES)
        irc.reply(resp.encode('utf8','ignore'))

    twit = wrap(twit, [getopts({'from':'something'}), optional('text')])

Class = Twitter


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
