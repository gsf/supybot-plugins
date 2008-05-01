import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import logging

from urllib2 import urlopen, urlparse, Request, build_opener, HTTPError
from urllib import urlencode
from urlparse import urlparse
import time
from BeautifulSoup import BeautifulSoup, StopParsing
import re

logger = logging.getLogger('supybot')

class RickCheck(callbacks.PluginRegexp,callbacks.Plugin):
    threaded = True
    regexps = ['ricksnarf']

    def __init__(self,irc):
        self.__parent = super(RickCheck, self)
        self.__parent.__init__(irc)

    def rickcheck(self, irc, msg, args, url):
        """<url> : does RickRoll detection on a URL
        """
        try:
            score, prob = self._rickscore(url)
        except Exception, e:
            irc.reply(e.message)
            return

        if (score >= 60):
            irc.reply('DANGER: RickRoll attempt in %s' % url)
        elif (score >= 30):
            irc.reply('WARNING: -possible- RickRoll attempt in %s' % url)
        else:
            irc.reply('no RickRoll detected in %s' % url)
        return

    rickcheck = wrap(rickcheck, ['text'])

    def _rickscore(self, url, score=0):

        parsed = urlparse(url)
        if not parsed[1]:
            return 0

        try:
            soup = self._url2soup(url)
            title = soup.find("title").string or ''
        except HTTPError, e:
            raise Exception, 'http error %s for %s' % (e.code, url)
        except (StopParsing, UnicodeDecodeError), e:
            raise Exception, 'parsing error "%s" for %s' % (e.reason, url)
        except Exception, e:
            logger.info('Got unexpected exception: %s, %s' % (e.__class__, e.message))
            raise Exception, 'something went wrong (bad url?): %s' % e

        patterns = {
            r'.*rickroll.*': 50,
            r'.*rick\s*astley.*': 40,
            r'.*never\s*gonna\s*give\s*you\s*up': 50,
            r'.*rick.+roll.*': 10
            }
        rickex = dict((re.compile(k, re.I | re.S), v) for k,v in patterns.items())
        score += sum([s for r,s in rickex.items() if soup(text=r)])

        meta = soup.find("meta", { "http-equiv" : "refresh" })
        if meta:
            logger.info('matched meta')
            score += 30

        maxscore = sum(patterns.values()) + 30 # 30 for the meta (meh?)
        prob = float(score) / float(maxscore) * 100
        logger.info('score %d, prob %f' % (score, prob))
        return score, int(prob)

    def ricksnarf(self, irc, msg, match):
        r"(?<!^@rickcheck )(https?://[-\w.]+\.[^\s]*)"
        url = match.group(1)
        self.log.info(url)

        try:
            score,prob = self._rickscore(url)
        except:
            return
        if prob > 20:
            irc.reply('WARNING: %s may be attempting a RickRoll (probability: %%%d)' % (msg.nick,prob), prefixNick=False)
        return

    def _url2soup(self, url, qsdata={}, postdata=None, headers={}):
        """
        Fetch a url and BeautifulSoup-ify the returned doc
        """
        logger.info("Fetching: %s" % url)
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        headers.update({'User-Agent': ua})
        params = urlencode(qsdata)
        if params:
            if '?' in url:
                url = "%s&%s" % (url,params)
            else:
                url = "%s?%s" % (url,params)
        req = Request(url,postdata,headers)
        doc = urlopen(req)
        data = doc.read()
        soup = BeautifulSoup(data)
        return soup

Class = RickCheck
