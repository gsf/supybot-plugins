###
# Copyright (c) 2010, Michael B. Klein
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.utils.web as web

from BeautifulSoup import BeautifulStoneSoup as BSS
from urllib import urlencode

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Wunderground Plugin; http://code4lib.org/irc)')

class Wunderground(callbacks.Plugin):

    def _fetch_xml(self, function, query):
      url = "http://api.wunderground.com/auto/wui/geo/%sXML/index.xml?%s" % (function, urlencode({'query' : query }))
      print url
      doc = web.getUrl(url, headers=HEADERS)
      # Wunderground double-encodes some of its entities, so we'll double-decode.
      return BSS(doc, convertEntities=BSS.HTML_ENTITIES)
    
    def _extract_text(self,node):
      return(BSS(' '.join(node.findAll(text=True)), convertEntities=BSS.HTML_ENTITIES).find(text=True))

    def _get_location_name(self, query):
      soup = self._fetch_xml("GeoLookup", query)
      location = [self._extract_text(soup.location.city),self._extract_text(soup.location.state)]
      return(', '.join([l.encode('utf-8') for l in location if l != None]))

    def wunder(self, irc, msg, args, query):
      """<location>
      
      Get the weather forecast for <location> from Weather Underground"""
      soup = self._fetch_xml("Forecast", query)
      result = ["Forecast for %s:" % self._get_location_name(query)]
      for day in soup.forecast.txt_forecast.findAll('forecastday'):
        result.append(': '.join([self._extract_text(day.title), self._extract_text(day.fcttext)]).encode('utf-8'))
      irc.reply(' '.join(result))

    wunder = wrap(wunder, ['something'])
    weather = wunder # FOR NOW
    
# TODO: Add a another method to report the simple/long-term forecast
    
Class = Wunderground


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
