import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError
import re

class RickCheck(callbacks.Privmsg):
    def rickcheck(self, irc, msg, args):
        """<url> (does RickRoll detection on a URL)
        """
        if len(args) != 1:
            irc.reply('usage: rickcheck <url>', prefixNick=True)
            return
        url = args.pop()
        opener = build_opener()
        html = None
        try:
            html = opener.open(url)
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True)
            return
        except:
            irc.reply('bad url: %s' % url, prefixNick=True)
            return
        soup = BeautifulSoup(html.read())
        title = soup.find("title").string
        rickex = re.compile(r'.*rick.*roll.*', re.IGNORECASE)
        if rickex.match(title):
            irc.reply('RickRoll detected in %s' % url, prefixNick=True)
            return
        meta = soup.find("meta", { "http-equiv" : "refresh" })
        if meta:
            irc.reply('possible RickRoll attempt in %s' % url, prefixNick=True)
            return
        irc.reply('no RickRoll detected in %s' % url, prefixNick=True)


Class = RickCheck

