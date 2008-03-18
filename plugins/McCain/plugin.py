import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener

class McCain(callbacks.Privmsg):
    def mccain(self, irc, msg, args):
        """grabs a line from http://www.johnmccainisyourjalopy.com/
        """
        url = 'http://www.johnmccainisyourjalopy.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('a').string.strip().upper())

Class = McCain

