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
import simplejson
from urllib import quote, urlencode

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Twitter Plugin; http://code4lib.org/irc)')
YWSID = "DxY8mcK-qiWxg953HoXVJg"

def _key_compare(a,b,key,boost = 1):
  if a[key] > b[key]:
    return 1 * boost
  elif a[key] == b[key]:
    return 0
  else:
    return -1 * boost
  
def _distance_compare(a,b):
  return _key_compare(a,b,'distance')
  
def _rating_compare(a,b):
  return _key_compare(a,b,'avg_rating',boost=-1)
    
class Yelp(callbacks.Plugin):
    """Add the help for "@plugin help Yelp" here
    This should describe *how* to use this plugin."""

    def _yelp_api(self, params):
      p = params.copy()
      p['ywsid'] = YWSID
      url = 'http://api.yelp.com/business_review_search?' + urlencode(p)
      doc = web.getUrl(url, headers=HEADERS)
      try:
          json = simplejson.loads(doc)
      except ValueError:
          return None
      return json

    def yelp(self, irc, msg, args):
      """<query> <location> [--sort relevance|rating|distance]
      Search Yelp
      """
      if len(args) < 2:
        raise callbacks.ArgumentError(None)
      else:
        result = self._yelp_api({'term' : args[0], 'location' : args[1]})
        if result == None:
          irc.reply('No results found for %s near %s' % (args[0],args[1]))
        else:
          businesses = result['businesses']
          if len(businesses) == 0:
            irc.reply('No results found for %s near %s' % (args[0],args[1]))
          try:
            if args[2] == '--sort':
              if args[3].lower().startswith('dist'):
                businesses.sort(_distance_compare)
              elif args[3].lower().startswith('rat'):
                businesses.sort(_rating_compare)
              elif args[3].lower().startswith('rel') == False:
                raise callbacks.ArgumentError('Unknown sort method: %s' % args[3])
          except IndexError:
            pass
          
          responses = []
          for business in businesses:
            half = business['avg_rating'] - int(business['avg_rating'])
            stars = unichr(0x2605) * int(business['avg_rating'])
            if half > 0:
              stars = stars + unichr(0x00BD)
            response = '%s (%s, %s [%.1fmi], %s, <%s>)' % (business['name'],business['address1'],business['city'],business['distance'],stars,business['url'])
            responses.append(response)
          irc.reply(' ; '.join(responses).encode('utf8','ignore'))

Class = Yelp


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
