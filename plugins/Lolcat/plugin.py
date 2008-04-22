import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError
import re

class Lolcat(callbacks.Privmsg):
    def lolify(self, irc, msg, args):
        """<text> translates text from English into a delightful lolcat pidgin!
        """
        if len(args) == 0:
            irc.reply('usage: lolify <text>', prefixNick=True)
            return
        text = " ".join(args)
        pidgin_map = (
            (r"\bthey are\b", 'they be'),
            (r"tions\b", 'shun'),
            (r"tions\b", 'shunz'),
            (r"tian\b", 'chun'),
            (r"tians\b", 'chunz'),
            (r"cket\b", 'kkit'),
            (r"ckets\b", 'kkitz'),
            (r"s\b", 'z'),
            (r"([^n])ew\b", '$1oed'),
            (r"([^yv])our\b", '$1ur'),
            (r"vour\b", 'vur'),
            (r"ing\b", 'in'),
            (r"([^rmea])y\b", '$1ee'),
            (r"got\b", "gotted"),
            (r"\bam\b", 'iz'),
            (r"\bmy\b", 'mah'),
            (r"\bno\b", 'noes'),
            (r"\bkitty\b", 'kitteh'),
            (r"\bcat\b", 'kitteh'),
            (r"\bwas\b", 'wuz'),
            (r"\bwith\b", 'wif'),
            (r"\bate\b", 'eated'),
            (r"\bhave\b", 'has'),
            (r"\bhead\b", 'hed'),
            (r"\bare\b", 'r'),
            (r"\bhi\b", 'hai'),
            (r"\bhello\b", 'hai'),
            (r"\bi'm\b", 'im'),
            (r"\byour\b", 'ur'),
            (r"\blove\b", 'luff'),
            (r"\byou\b", 'u'),
            (r"\bwork\b", 'wurk'),
            (r"\band\b", 'an'),
            (r"\bthe\b", 'teh'),
            (r"\bdude\b", 'd00d'),
        )
        for pattern in pidgin_map:
            p = re.compile(pattern[0], re.IGNORECASE)
            text = p.sub(pattern[1], text)
        irc.reply(text, prefixNick=True)

    def randlol(self, irc, msg, args):
        self.lolrand(irc, msg, args)

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
            irc.reply('http error %s for random lolcat' % (e.code), prefixNick=True)
            return
        soup = BeautifulSoup(html)
        anchor = soup.find("div", "post").h1.a
        text = re.sub(r'&nbsp;', ' ', anchor.string)
        href = anchor['href']
        irc.reply("%s <%s>" % (text, href), prefixNick=True)

Class = Lolcat

