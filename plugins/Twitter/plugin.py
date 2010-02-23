
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

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Twitter Plugin; http://code4lib.org/irc)')

class Twitter(callbacks.Plugin):
    """Add the help for "@plugin help Twitter" here
    This should describe *how* to use this plugin."""
    threaded = True

    def _shorten_urls(self, s):
      result = s
      urlreg = re.compile('[a-z]+://[^\s\[({\]})]+')
      for longUrl in urlreg.findall(s):
        if len(longUrl) > 22:
          params = { 'longUrl' : longUrl, 'login' : 'zoia', 'apiKey' : 'R_e0079bf72e9c5f53bb48ef0fe706a57c',
            'version' : '2.0.1', 'format' : 'json' }
          url = 'http://api.bit.ly/shorten?' + urlencode(params)
          response = self._fetch_json(url)
          shortUrl = response['results'][longUrl]['shortUrl']
          result = result.replace(longUrl,shortUrl)
      return(result)
      
    def _fetch_json(self, url):
        doc = web.getUrl(url, headers=HEADERS)
        try:
            json = simplejson.loads(doc)
        except ValueError:
            return None
        return json
        
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

    def _twitter_api(self, path, params, post = False):
      auth_handler = urllib2.HTTPBasicAuthHandler()
      auth_handler.add_password("Twitter API", "http://api.twitter.com", "bot4lib", "zoiaftw")
      http = urllib2.build_opener(auth_handler)
      url = "http://api.twitter.com/1/%s.json" % path
      data = urlencode(params)

      print '?'.join((url,data))
      if post:
        handle = http.open(url,data)
      else:
        handle = http.open('?'.join((url,data)))
      resp = handle.read()
      return(simplejson.loads(resp))
      
    def tweet(self, irc, msg, args, user, text):
      """<text>

      Post to the @bot4lib Twitter account"""
#      tweet_text = '<%s> %s' % (user.name, text)
      tweet_text = self._shorten_urls(text)
      if len(tweet_text) <= 140:
        self._twitter_api('statuses/update', { 'status' : tweet_text }, post=True)
        url = "http://api.twitter.com/1/statuses/update.json"
        irc.reply('The operation succeeded.')
      else:
        irc.reply('Tweet too long!')

    tweet = wrap(tweet, ['user','text'])

    last_mention = None
    def mentions(self, irc, msg, args):
      params = {}
      if self.last_mention != None:
        params['since_id'] = self.last_mention
      tweets = self._twitter_api('statuses/mentions', params)
      responses = []
      if tweets:
        self.last_mention = tweets[0]['id']
        for tweet in tweets:
          responses.append('@%s: %s' % (tweet['user']['screen_name'],tweet['text']))
        irc.reply(' ; '.join(responses), prefixNick=False)
      else:
        irc.reply('No new mentions')
      
Class = Twitter


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
