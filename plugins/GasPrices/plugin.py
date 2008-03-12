import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError
import re

class GasPrices(callbacks.Privmsg):
    def gasprices(self, irc, msg, args):
        """<zipcode> [<number_of_results(1-5)>]

        lists cheapest gas prices by zip code
        """
        MAX_RESULTS = 5

        if len(args) not in [1, 2]:
            irc.reply("usage: gasprices <zipcode> [<number_of_results(1-5)>]", prefixNick=True)
            return
        zipcode = args[0]
        # there has got to be a cleaner, more pythonic way to do this
        number_of_results = None
        if len(args) == 2:
            if args[1] not in ["1", "2", "3", "4", "5"]:
                irc.reply("usage: gasprices <zipcode> [<number_of_results(1-5)>]", prefixNick=True)
                return
            else:
                number_of_results = args[1]
        else:
            number_of_results = 1

        baseurl = 'http://autos.msn.com/everyday'
        url = 'http://autos.msn.com/everyday/gasstations.aspx?zip=%s' % zipcode
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = None
        try:
            html = opener.open(url)
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True)
            return
        soup = BeautifulSoup(html)
        i = 0
        responses = []
        for result in soup.find("table", id="tblDetail")('tr')[1:number_of_results + 1]:
            i += 1
            anchor = result('td')[1]('div')[1]('a').pop()
            station = anchor.string
            map = "%s/%s" % (baseurl, anchor['href'])
            address = result('td')[2]('span')[0].string + " " + result('td')[2]('span')[1].string
            price = result('td')[3]('span')[0].string
            # date = result('td')[3]('span')[1].string
            responses.append("%s. %s at %s (%s) <%s>" % (i, price, station, address, map))
        irc.reply("cheapest gas in %s (%s result(s)): %s" % (zipcode, number_of_results, " | ".join(responses)), prefixNick=True)

Class = GasPrices

