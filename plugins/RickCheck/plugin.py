import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError
import re

def rickroll_detect(url):
    doc = None
    soup = None
    title = ''
    
    opener = build_opener()
    
    try:
        doc = opener.open(url)
    except HTTPError, e:
        return 'http error %s for %s' % (e.code, url)
    except:
        return 'bad url: %s' % url
    
    doc = doc.read()
    try:
        soup = BeautifulSoup(doc)
    except:
        return 'could not parse %s' % url
    
    try:
        title = soup.find("title").string
    except:
        pass

    rickex = re.compile(r'rick.*roll', re.IGNORECASE | re.DOTALL)
    if rickex.search(title) or rickex.search(doc):
        return 'DANGER: RickRoll detected in %s' % url
    
    meta = soup.find("meta", { "http-equiv" : "refresh" })
    if meta:
        url_regex = re.compile(r'url\s*=\s*(.+)', re.IGNORECASE)
        match = url_regex.search(meta['content'])
        if match:
            rickroll_detect(match.groups()[0])

    return 'no RickRoll detected in %s' % url


class RickCheck(callbacks.Privmsg):
    def rickcheck(self, irc, msg, args):
        """<url> (does RickRoll detection on a URL)
        """
        if len(args) != 1:
            irc.reply('usage: rickcheck <url>', prefixNick=True)
            return
        url = args.pop()
        irc.reply(rickroll_detect(url), prefixNick=True)

Class = RickCheck

