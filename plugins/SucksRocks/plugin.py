###
# Copyright (c) 2008, Michael B. Klein
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
from urllib2 import urlopen, Request, HTTPError
from urllib import urlencode
import simplejson

class SucksRocks(callbacks.Plugin):
    pass

    def rate(self, irc, msg, args):
        """<term1> <term2> ...
        Rates terms according to the criteria at http://www.sucks-rocks.com/
        """
        
        if len(args) == 0:
            irc.reply('(rate <term1> <term2> ...) -- Rates terms according to the criteria at http://www.sucks-rocks.com/', prefixNick=True)
        else:
            msg = []
            min_rating = { 'term':None, 'rating':5.0 }
            max_rating = { 'term':None, 'rating':5.0  }
            for t in args:
                term = t.replace('_',' ').replace('+',' ')
                url = 'http://www.sucks-rocks.com/query?' + urlencode({'term':term})
                try:
                    json = urlopen(Request(url, None, {'Accept': 'application/json'})).read()
                except HTTPError:
                    json = '{"term": "' + term + '", "sucks": 0, "rocks": 0 }'
                ratings = simplejson.loads(json)
                sucks = float(ratings['sucks'])
                rocks = float(ratings['rocks'])
                if (sucks == 0) and (rocks == 0):
                    msg.append(term + ': ?')
                else:
                    rating = ((rocks / (sucks + rocks)) * 10)
                    result = { 'term':term, 'rating':rating }
                    if result['rating'] < min_rating['rating']:
                        min_rating = result
                    if result['rating'] > max_rating['rating']:
                        max_rating = result
                
                    msg.append('%(term)s: %(rating)2.1f' % result)
        
            response = '; '.join(msg) + '.'
            if min_rating['term'] != max_rating['term']:
                if min_rating['term'] != None:
                    response += ' ' + min_rating['term'] + ' sucks!'
                if max_rating['term'] != None:
                    response += ' ' + max_rating['term'] + ' rocks!'

            irc.reply(response.encode('utf-8'), prefixNick=True)

Class = SucksRocks


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
