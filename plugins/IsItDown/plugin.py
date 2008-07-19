import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener

class IsItDown(callbacks.Privmsg):
    def isitdown(self, irc, msg, args, url):
        """
        <url>: Returns the response from http://www.downforeveryoneorjustme.com/
        """
        site = 'http://downforeveryoneorjustme.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        try:
            html = opener.open(site + url)
            html_str = html.read()
            soup = BeautifulSoup(html_str)
            response = soup.div.contents[0].strip()
            irc.reply(response, prefixNick=True)
        except urllib2.HTTPError, oops:
            irc.reply("Hmm. downforeveryoneorjustme.com returned the following error: [%s]" % (oops), prefixNick=True)
        except AttributeError:
            irc.reply("Hmm. downforeveryoneorjustme.com probably changed its response format; please update me.", prefixNick=True)
    isitdown = wrap(isitdown, ['text'])

Class = IsItDown

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
