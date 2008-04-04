import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError
import re

def validate_url(url):
    doc = None
    soup = None
    ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.13'
    opener = build_opener()
    opener.addheaders = [('User-Agent', ua)]
    
    try:
        doc = opener.open(url)
    except HTTPError, e:
        reply('http error %s for %s' % (e.code, url))
    except:
        reply('bad url: %s' % url)
    
    doc = doc.read()
    try:
        soup = BeautifulSoup(doc)
    except:
        reply('could not parse %s' % url)

    return soup

    
def reply(message):
    self.irc.reply(message, prefixNick=True)
    exit()


def detect_rickroll(soup):
    title = ''
    try:
        title = soup.find("title").string
    except:
        pass

    rickex = re.compile(r'rick.*roll', re.IGNORECASE | re.DOTALL)
    return rickex.search(title) or rickex.search(str(soup))

def detect_meta(soup):
    meta = soup.find("meta", { "http-equiv" : "refresh" })

    if meta:
        url_regex = re.compile(r'url\s*=\s*(.+)', re.IGNORECASE)
        match = url_regex.search(meta['content'])
        if match:
            return match.groups()[0]

    return False

def check_url(url):
    soup = validate_url(url)
    if detect_rickroll(soup):
        reply('DANGER: RickRoll detected in %s' % url)
        
    meta_url = detect_meta(soup)
    if not meta_url:
        reply('no RickRoll detected in %s' % url)
    else:
        rickcheck(meta_url)

class RickCheck(callbacks.Privmsg):
    def __init__(self, irc):
        self.__parent = super(RickCheck, self)
        self.__parent.__init__(irc)
        self.irc = irc

    def rickcheck(self, irc, msg, args):
        """<url> (does RickRoll detection on a URL)
        """
        if len(args) != 1:
            self.irc.reply('usage: rickcheck <url>', prefixNick=True)
            return
        url = args.pop()
        check_url(url)

Class = RickCheck
