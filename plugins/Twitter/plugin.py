import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import calendar
from random import randint
import re
import sys
import simplejson
import supybot.utils.web as web
import time
import urllib2
from urllib import urlencode, quote
from cgi import parse_qs
from BeautifulSoup import BeautifulStoneSoup as BSS
import lxml.html
from oauth import oauth

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Twitter Plugin; http://code4lib.org/irc)')

class Twitter(callbacks.Plugin):
    """Add the help for "@plugin help Twitter" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
      self.__parent = super(Twitter, self)
      self.__parent.__init__(irc)
      self.last_mention = None
      self.last_request = 0
        
    def __call__(self, irc, msg):
      self.__parent.__call__(irc, msg)
      now = time.time()
      wait = self.registryValue('waitPeriod')
      if now - self.last_request > wait:
        self.last_request = now
        irc = callbacks.SimpleProxy(irc, msg)
        responses = self._get_mentions(maxAge=7200)
        if len(responses) > 0:
          irc.reply(' ; '.join(responses), to='#code4lib', prefixNick=False)

    def _get_mentions(self, maxAge = None):
      params = {}
      if self.last_mention != None:
        params['since_id'] = self.last_mention
      tweets = self._twitter_api('statuses/mentions', params)
      responses = []
      if tweets:
        now = time.time()
        self.last_mention = tweets[0]['id']
        for tweet in tweets:
          age = now - calendar.timegm(time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
          if (maxAge is None) or (age <= maxAge):
            responses.append('<%s> %s' % (tweet['user']['screen_name'],tweet['text']))
        responses.reverse()
      return responses
        
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

    def tweep(self, irc, msg, args, user):
        """
        @tweep [user]

        Get stats on a twitter user
        """
        url = 'http://api.twitter.com/1/users/show/%s.json' % user
        userdata = self._fetch_json(url)
        if not userdata:
            irc.reply("Twitter don't know 'nuthin about %s" % user)
            return
        resp = '; '.join([
            'name: %s' % userdata['name'],
            'description: %s' % userdata['description'],
            'location: %s' % userdata['location'],
            'followers: %s' % userdata['followers_count'],
            'following: %s' % userdata['friends_count'],
        ])
        irc.reply(resp.encode('utf-8'), prefixNick=False)

    tweep = wrap(tweep, ['text'])

    def twit(self, irc, msg, args, opts, query):
        """
        @twit [--from user] [--id tweet_id] [query]

        Return the last three tweets matching a given string 
        and/or user. if no query specified returns a random tweet from 
        the public timeline if no options given.
        """

        screen_name = None
        tweet_id = None
        
        for (opt, arg) in opts:
            if opt == 'from':
                screen_name = arg
            if opt == 'id':
                tweet_id = arg
                
        
        def recode(text):
            return BSS(text.encode('utf8','ignore'), convertEntities=BSS.HTML_ENTITIES)
            
        resp = 'Gettin nothin from teh twitter.'
        if tweet_id:
            url = 'http://api.twitter.com/1/statuses/show/%s.json' % (tweet_id)
            tweet = self._fetch_json(url)
            resp = "<%s> %s" % (tweet['user']['screen_name'], recode(tweet['text']))
        elif query:
            if screen_name:
                query = "from:%s %s" % (screen_name, query)
            url = 'http://search.twitter.com/search.json?' 
            json = self._fetch_json(url + urlencode({ 'q': query, 'rpp': 3 }))
            try:
                tweets = json['results']
                extracted = ["<%s> %s" % (x['from_user'], recode(x['text'])) for x in tweets]
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
                resp = "%s: %s" % (tweet['user']['screen_name'], recode(tweet['text']))
        irc.reply(resp.replace('\n',' ').strip(' '))

    twit = wrap(twit, [getopts({'from':'something','id':'something'}), optional('text')])
    
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
      consumer = oauth.OAuthConsumer('BahWsa9ynBogaXxRoJPX5Q', '5bWdyET8iFpFUlpFuFJV02NOILoKEn5u6jt7TwXoXI')
      token = oauth.OAuthToken('116458525-eI3WNzzatAm4S7DjYzX5fjOCr1wGyY0NtrOdfOqk','H0I2F1cvL8Z421isUW4nARTgEC0nbDBFCmF4lLoE')
      client = oauth.OAuthClient(consumer,token)
      
      url = "http://api.twitter.com/1/%s.json" % path
      body = urlencode(params)
      if post:
        method = 'POST'
      else:
        method = 'GET'
        
      oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method=method, http_url=url, parameters=params)
      oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, token)

      body = None
      if post:
        body = oauth_request.to_postdata()
      else:
        url = oauth_request.to_url()

      handle = urllib2.urlopen(url, body)
      content = handle.read()
      
      return(simplejson.loads(content))
      
    def tweet(self, irc, msg, args, user, text):
      """<text>

      Post to the @bot4lib Twitter account"""
#      tweet_text = '<%s> %s' % (user.name, text)
      tweet_text = self._shorten_urls(text)
      if len(tweet_text) <= 140:
        self._twitter_api('statuses/update', { 'status' : tweet_text }, post=True)
        irc.reply('The operation succeeded.')
      else:
        irc.reply('Tweet is %s characters too long!' % (len(tweet_text) - 140))

    tweet = wrap(tweet, ['user','text'])

    def untweet(self, irc, msg, args, user, tweet_id):
      response = self._twitter_api('statuses/destroy/%s.json' % tweet_id)
      irc.reply('OK!')
      
    untweet = wrap(untweet, ['text'])
      
    def mentions(self, irc, msg, args):
      responses = self._get_mentions();
      if len(responses) > 0:
        irc.reply(' ; '.join(responses), prefixNick=False)
      else:
        irc.reply('No new mentions')

    def twanalyze(self, irc, msg, args, user):
        """@twanalyze user

        See the http://twanalsyt.com personality test result
        for any twitter user
        """
        url = 'http://twanalyst.com/%s' % quote(user)
        doc = web.getUrl(url, headers=HEADERS)
        html = lxml.html.fromstring(doc)
        try:
            link = html.xpath('//a[contains(@href, "twitter.com/?status")]')[0]
            href = link.attrib['href']
            parsed = parse_qs(href)
            status = parsed['http://twitter.com/?status'][0]
            m = re.match('My Twitter personality: (.+?) My style: (.+?) ([A-Z]+)', status)
            resp = "Personality: %s, Style: %s, Ranking: %s" % m.groups()
            irc.reply(resp)
        except Exception, e:
            print >>sys.stderr, e
            irc.reply('blerg! scraping FAIL')

    twanalyze = wrap(twanalyze, ['text'])
    
    def hashtag(self, irc, msg, args, tag):
      """<tag>
      
      Look up <tag> on tagal.us"""
      key = re.sub('^#','',tag)
      response = self._fetch_json('http://api.tagal.us/tag/%s/show.json' % (key))
      if response is None:
        irc.reply('No entry for hashtag "%s" at tagal.us' % (tag), prefixNick=True)
      else:
        irc.reply(response['definition']['the_definition'].strip(), prefixNick=True)
    
    hashtag = wrap(hashtag, ['somethingWithoutSpaces'])
      
      
Class = Twitter


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
