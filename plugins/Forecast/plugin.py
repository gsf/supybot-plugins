import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError

class Forecast(callbacks.Privmsg):

    def forecast(self, irc, msg, args, zipcode):
        """
        <zipcode>: Returns the response from http://www.thefuckingweather.com/
        """
        site = 'http://www.thefuckingweather.com/?zipcode=%s' % zipcode
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        try:
            html = opener.open(site)
            html_str = html.read()
            soup = BeautifulSoup(html_str)
            response = u' '.join(soup.find('div', 'large').findAll(text=True))
            response.replace('&deg;', u'°')
            irc.reply(response, prefixNick=True)
        except:
            irc.reply("Man, I have no idea; things blew up real good.", prefixNick=True)

    forecast = wrap(forecast, ['text'])

Class = Forecast
