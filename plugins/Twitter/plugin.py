
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from random import randint
import re
import simplejson
import supybot.utils.web as web
import urllib2
from urllib import urlencode, quote
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
        irc.reply(resp.encode('utf8','ignore').replace('\n',' ').strip(' '))

    trends = wrap(trends, [optional('text')])

    def _fetch_json(self, url):
        doc = web.getUrl(url, headers=HEADERS)
        try:
            json = simplejson.loads(doc)
        except ValueError:
            return None
        return json
        
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

        resp = 'Gettin nothin from teh twitter.'
        if query:
            if screen_name:
                query = "from:%s %s" % (screen_name, query)
            url = 'http://search.twitter.com/search.json?' 
            json = self._fetch_json(url + urlencode({ 'q': query, 'rpp': 3 }))
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
            tweets = self._fetch_json(url)
            if tweets:
                tweet = tweets[0] #randint(0, len(tweets)-1)]
                resp = "%s: %s" % (tweet['user']['screen_name'], tweet['text'])
        resp = BSS(resp, convertEntities=BSS.HTML_ENTITIES)
        irc.reply(resp.encode('utf8','ignore').replace('\n',' ').strip(' '))

    twit = wrap(twit, [getopts({'from':'something'}), optional('text')])
    
    def tweet(self, irc, msg, args, user, text):
      """<text>
      
      Post to the @bot4lib Twitter account"""
#      tweet_text = '<%s> %s' % (user.name, text)
      tweet_text = text
      if len(tweet_text) <= 140:
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password("Twitter API", "http://api.twitter.com", "bot4lib", "zoiaftw")
        http = urllib2.build_opener(auth_handler)
        
        url = "http://api.twitter.com/1/statuses/update.json"
        data = urlencode({ 'status' : tweet_text })
        handle = http.open(url,data)
        resp = handle.read()
        irc.reply('The operation succeeded.')
      else:
        irc.reply('Tweet too long!')
      
    tweet = wrap(tweet, ['user','text'])
    
    def trend(self, irc, msg, args, query):
      """[<query>]
      
      Explain why <query> is trending on Twitter, according to whatthetrend.com. An empty
      query lists current trending topics."""
      if (query is None) or (query == ''):
        url = 'http://www.whatthetrend.com/api/trend/listAll/json'
        json = self._fetch_json(url)
        trends = json['api']['trends']['trend']
        extracted = [trend['name'] for trend in trends]
        resp = '; '.join(["%d. %s" % t for t in zip(range(1, len(extracted) + 1), extracted)])
      else:
        url = 'http://www.whatthetrend.com/api/trend/getByName/%s/json' % quote(query)
        json = self._fetch_json(url)
        try:
          trend = json['api']['trend']
          try:
            explanation = trend['blurb']['text']
          except TypeError:
            explanation = 'Unexplained trend'
          resp = '%s - %s (%s)' % (trend['name'], explanation, trend['links']['tinyUrl'])
        except KeyError:
          resp = '%s - %s' % (query, json['api']['error'])
      irc.reply(resp.encode('utf8','ignore'))
      
    trend = wrap(trend, [optional('text')])

Class = Twitter


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
