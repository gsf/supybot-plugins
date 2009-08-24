###
# Copyright (c) 2009, Michael B. Klein
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
import re
import simplejson
from urllib import urlencode, urlopen, unquote_plus
from booze import *

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; AlcoholPoisoning Plugin; http://code4lib.org/irc)')

class AlcoholPoisoning(callbacks.Plugin):
    """Add the help for "@plugin help AlcoholPoisoning" here
    This should describe *how* to use this plugin."""
    
    def booze(self, irc, msg, args, weight, sex, drink):
      """<weight>[lbs|kg] <m[ale]|f[emale]> <drink>
            
      Calculates how many <drink>s it would take to kill you. Use 'list' or 'search <regex>' to get a list of known drinks."""
      print weight + "\n"
      if weight == 'list':
        if (sex in beverages.keys()):
          responseList = beverages[sex].keys()
          responseList.sort()
          irc.reply(', '.join(responseList))
        else:
          responseList = beverages.keys()
          response = 'list [' + '|'.join(responseList) + ']'
          irc.reply(response)
      elif weight == 'search':
        regex = re.compile(sex,re.IGNORECASE)
        matches = []
        for beverage in beverage_codes:
          if re.search(regex,beverage):
            matches.append(beverage)
        matches.sort()
        irc.reply(', '.join(matches))
      else:
        if not drink:
          irc.reply('Check yer *hic* syntax, mate.')
        else:
          try:
            split_weight = re.split("([0-9]+)(.*)",weight)
            weight = split_weight[1]
            units = split_weight[2] or 'lbs'
          
            params = urlencode(dict(
              beverage    = beverage_codes[drink],
              weight      = weight,
              weight_type = unit_codes[units],
              gender      = gender_codes[sex or 'm']
            ))
            json = unquote_plus(urlopen("http://www.barstools.net/booze_death/",params).read())
            data = simplejson.loads(json)
            amount = data['lethal_drinks']
            irc.reply("It would take " + amount + " to kill you.", prefixNick=True)
          except KeyError:
            irc.reply(drink + "? Wha's tha'?")
      
    booze=wrap(booze, ['something', optional('something'), optional('text')])

Class = AlcoholPoisoning


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
