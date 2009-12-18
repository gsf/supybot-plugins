###
# Copyright (c) 2009, lbjay
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.utils.web as web

import re
from lxml.html.soupparser import fromstring
from lxml.cssselect import CSSSelector
from datetime import datetime

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Astro Plugin; http://code4lib.org/irc)')

class Astro(callbacks.Plugin):
    """Add the help for "@plugin help Astro" here
    This should describe *how* to use this plugin."""
    threaded = True

    def asteroid(self, irc, msg, args):
        au2miles = 92955887.6
        url = 'http://www.cfa.harvard.edu/iau/lists/PHACloseApp.html'
        
        # stupid astronomers and their stupid <pre> data
        # example of parsed pha
        # ('2002 AT4  ',        => object name
        #  '2511159.67',        => julian date
        #  '2163 Mar. 22.17',   => calendar date
        #  '0.05000')           => distance in AU
        pattern = re.compile('\s*([\(\)\w ]+?  )\s*([\d\.]+)\s*(\d{4} [a-z\.]+\s*[\d\.]+)\s*([\d\.]+)', re.I)

        html = web.getUrl(url, headers=HEADERS)
        tree = fromstring(html)
        pre = tree.xpath('//pre')[0]
        lines = pre.text.split('\n')[3:]
        lines = [l for l in lines if len(l)]
        phas = [re.match(pattern, l).groups() for l in lines]
        phas.sort(lambda a,b: cmp(a[1], b[1]))
        (name, jd, date, au) = phas[0]                
        date = date.replace('.', ' ')
        # the %j is just a placeholder
        date = datetime.strptime(date, "%Y %b %d %j")
        miles = float(au) * au2miles
        resp = "Object '%s' will pass within %s miles of earth on %s"
        irc.reply(resp % (name.strip(), miles, date.strftime("%c")))

Class = Astro


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
