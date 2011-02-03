###
# Copyright (c) 2011, Michael B. Klein
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

import simplejson
import supybot.utils.web as web
import time
import urllib2
from urllib import urlencode, quote
from BeautifulSoup import BeautifulStoneSoup as BSS

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Twitter Plugin; http://code4lib.org/irc)')

class TwitterSnarfer(callbacks.PluginRegexp):
  regexps = ['tweetSnarfer']

  def _fetch_json(self, url):
      doc = web.getUrl(url, headers=HEADERS)
      try:
          json = simplejson.loads(doc)
      except ValueError:
          return None
      return json

  def tweetSnarfer(self, irc, msg, match):
    r'http://(?:www\.)?twitter\.com.*/status/([0-9]+)'
    print match.group(1)
    tweet_id = match.group(1)
  
    def recode(text):
        return BSS(text.encode('utf8','ignore'), convertEntities=BSS.HTML_ENTITIES)
        
    resp = 'Gettin nothin from teh twitter.'
    url = 'http://api.twitter.com/1/statuses/show/%s.json' % (tweet_id)
    print url
    tweet = self._fetch_json(url)
    resp = "<%s> %s" % (tweet['user']['screen_name'], recode(tweet['text']))
    irc.reply(resp.replace('\n',' ').strip(' '), prefixNick=False)

Class = TwitterSnarfer


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
