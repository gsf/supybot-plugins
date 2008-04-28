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
        self._guard_up = False

    def rickguard(self, irc, msg, args, cmd):
        """
        <on|off> : enable or disable automatic rickroll detection
        """
        if cmd == 'on':
            self._guard_up = True
            irc.reply("RickGuard enabled!")
        elif cmd == 'off':
            self._guard_up = False
            irc.reply("RickGuard disabled!")
        else:
            if self._guard_up:
                status = 'enabled'
            else:
                status = 'disabled'
            irc.reply("Rickguard status: %s" % status)
        return

    rickguard = wrap(rickguard, [optional('text')])

    def rickcheck(self, irc, msg, args, url):
        """<url> : does RickRoll detection on a URL
        """
        try:
            score = self._rickscore(url)
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
        except HTTPError, e:
            raise Exception, 'http error %s for %s' % (e.code, url)
        except (StopParsing, UnicodeDecodeError), e:
            raise Exception, 'parsing error "%s" for %s' % (e.reason, url)
        except Exception, e:
            logger.info('Got unexpected exception: %s, %s' % (e.__class__, e.message))
            raise Exception, 'something went wrong (bad url?): %s' % e

        title = soup.find("title").string or ''
        rickex = re.compile(r'.*rick.*roll.*', re.IGNORECASE | re.DOTALL)

        if rickex.match(title):
            score += 60
        if rickex.match(soup.__str__()):
            score += 30
        meta = soup.find("meta", { "http-equiv" : "refresh" })
        if meta:
            score += 30
        return score

    def ricksnarf(self, irc, msg, match):
        r"(?<!^rickcheck )(https?)://[-\w.]+\.[^\s]*"
        url = match.group(1)

        if not self._guard_up:
            return
            
        try:
            score = self._rickscore(url)
        except:
            return
        if score > 20:
            irc.reply('WARNING: %s may be attempting a RickRoll' % msg.nick)
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
