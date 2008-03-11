import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError
import re

class Lolcat(callbacks.Privmsg):
    def randlol(self, irc, msg, args):
        lolrand(self, irc, msg, args)

    def lolrand(self, irc, msg, args):
        """prints out a random lolcat phrase
        """
        url = 'http://icanhascheezburger.com/?random'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        # yes, this is poor design
        html = None
        try:
            html = opener.open(url)
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, location), prefixNick=True)
            return
        soup = BeautifulSoup(html)
        anchor = soup.find("div", "post").h1.a
        text = re.sub(r'&nbsp;', ' ', anchor.string)
        href = anchor['href']
        irc.reply("%s <%s>" % (text, href), prefixNick=True)

Class = Lolcat

