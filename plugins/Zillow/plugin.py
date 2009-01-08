###
# Copyright (c) 2009, JayL
# All rights reserved.
#
#
###

import supybot.utils as utils
import supybot.utils.web as web
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import simplejson

API_URL = 'http://www.zillow.com/webservice/%s.htm?zws-id=%s&output=json'
ZWSID = 'X1-ZWz1crn3j8npjf_1sm5d'
HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Sing Plugin; http://code4lib.org/irc)')

class Zillow(callbacks.Plugin):
    """Add the help for "@plugin help Zillow" here
    This should describe *how* to use this plugin."""
    threaded = True

    def mortgage(self, irc, msg, args):
        """
        Returns latest mortgage rates summary from Zillow --
        http://www.zillow.com/howto/api/APIOverview.htm
        """
        url = API_URL % ('GetRateSummary', ZWSID)
        json = web.getUrl(url, headers=HEADERS)
        response = simplejson.loads(json)
        rates = response['response']

        o = "The average rate on a 30 year mortgage is %s. Last week it was %s. " + \
        "If you want a 15 year mortgage the average rate is %s. Last week it was %s. " + \
        "If you're crazy enough to want a 5-1 ARM the average rate is %s. Last week it was %s. " + \
        "This is according to the Zillow Mortgage Market."

        resp = o % (
            rates['today']['thirtyYearFixed'], rates['lastWeek']['thirtyYearFixed'],
            rates['today']['fifteenYearFixed'], rates['lastWeek']['fifteenYearFixed'],
            rates['today']['fiveOneARM'], rates['lastWeek']['fiveOneARM'])
        
        irc.reply(resp)

Class = Zillow

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
