import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError

class Motivate(callbacks.Privmsg):
    def motivate(self, irc, msg, args):
        """
        Just before you slit your throat, get an inspirational quote!
        """
        site = 'http://www.marchnet.co.uk/random-inspiration.php'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        try:
            html = opener.open(site)
            html_str = html.read()
            soup = BeautifulSoup(html_str)
            response = str(soup('p')[0])
            quote = re.search(r'^.*?"(.*?)"', response, re.S).group(1)
            quote = quote.replace('\n', ' ').rstrip()
            quote = quote.replace("'", '')
            response = str(soup('i')[0])
            attrib = re.search(r'^.*?\((.*?)\)', response, re.S).group(1)
            attrib = attrib.replace('\n', ' ').lstrip()

            if not quote:
                raise AttributeError("Didn't find a quote")
            if not attrib:
                raise AttributeError("Didn't find an attribution")

            irc.reply("%s - %s" % (quote, attrib))

        except HTTPError, oops:
            irc.reply("Hmm. %s returned the following error: [%s]" % (site, str(oops)), prefixNick=True)
        except AttributeError:
            irc.reply("Hmm. %s probably changed its response format; please update me." % (site), prefixNick=True)
        except:
            irc.reply("Man, I have no idea; things blew up real good.", prefixNick=True)

Class = Motivate

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
