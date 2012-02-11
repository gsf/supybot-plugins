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
import supybot.ircdb as ircdb
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import random
import re
import time
import simplejson
import supybot.utils.web as web
import urllib

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Github Plugin; http://code4lib.org/irc)')
TMDBK = '2aa9fc67c6ce2fe64313d34806e4f59e'
FREEBASE_TYPES = {
  'movie': {
    'type': '/film/film',
    'subquery': { '/film/film/starring': [{'character~=':'.', 'character':None, 'index':None, 'sort': 'index'}] },
    'extractor': lambda r: [c['character'] for c in r['/film/film/starring']]
  },
  'tv': {
    'type': '/tv/tv_program',
    'subquery': { 'tv/tv_program/regular_cast': [{'character~=':'.', 'character':None, 'index':None, 'sort': 'index'}] },
    'extractor': lambda r: [c['character'] for c in r['/tv/tv_program/regular_cast']]
  },
  'play': {
    'type': '/theater/play',
    'subquery': { 'characters': [] },
    'extractor': lambda r: r['characters']
  },
    'book': {
    'type': '/book/book',
    'subquery': { 'characters': [] },
    'extractor': lambda r: r['characters']
  }
}

class Cast(callbacks.Plugin):
      
    def _query_tmdb(self, cmd, args):
      url = "http://api.themoviedb.org/2.1/%s/en/json/%s/%s" % (cmd,TMDBK,urllib.quote(str(args)))
      doc = web.getUrl(url, headers=HEADERS)
      try:
        json = simplejson.loads(doc)
      except ValueError:
        return None
      return json
    
    def tmdb(self, irc, msg, args, channel, opts, play):
      """[<movie>]
      Cast <movie> from the current channel participants using information retrieved from themoviedb.org."""
      random.seed()
      nicks = list(irc.state.channels[channel].users)
      random.shuffle(nicks)
      
      maxlen = 20
      for (opt,arg) in opts:
        if opt == 'max':
          maxlen = int(arg)
      
      parts = None
      record = None
      data = self._query_tmdb('Movie.search',play)
      if data != None and data[0] != 'Nothing found.':
        best = data[0]
        for r in data:
          if r['name'].lower().strip() == play.lower().strip():
            best = r
            break
        movie = self._query_tmdb('Movie.getInfo',best['id'])[0]
        title = movie['name']
        parts = []
        for entry in movie['cast']:
          if entry['job'] == 'Actor':
            if re.match(r'^(((him|her|it)self)|themselves)$', entry['character'], re.I):
              parts.append(entry['name'])
            else:
              parts.append(entry['character'])
            if len(parts) == maxlen:
              break

      if record is not None:
        title = record.play
        parts = re.split(r'\s*;\s*',record.cast)
      
      if parts is not None:
        if len(parts) > len(nicks):
          irc.reply('Not enough people in %s to cast "%s"' % (channel, title))
        else:
          parts.reverse()
          response = '%s presents "%s", starring ' % (channel, title)
          while len(parts) > 1:
            response += "%s as %s, " % (nicks.pop(), parts.pop())
            if len(parts) == 1:
              response += "and "
          response += "%s as %s." % (nicks.pop(), parts.pop())
          irc.reply(response.encode('utf8'), prefixNick=False)
      else:
        irc.reply('I don\'t know "%s"!' % play)
    tmdb = wrap(tmdb, ['channeldb', getopts({'max':'int'}), 'text'])
    
    def _query_freebase(self, work_type, thing):
      props = FREEBASE_TYPES[work_type]
      url = "https://api.freebase.com/api/service/search?query=%s&type=%s" % (web.urlquote(thing),props['type'])
      response = simplejson.loads(web.getUrl(url, headers=HEADERS))
      if len(response['result']) == 0:
        return None
      else:
        fbid = response['result'][0]['id']
        query = {
          'escape': False,
          'query': {
            "id": fbid,
            "type": props['type'],
            "name": None,
            "limit": 1
          }
        }
        query['query'].update(props['subquery'])
        url = "https://api.freebase.com/api/service/mqlread?query=%s" % web.urlquote(simplejson.dumps(query))
        response = simplejson.loads(web.getUrl(url, headers=HEADERS))
        result = response['result']
        if result is None:
          return None
        else:
          return({
            'url': "http://www.freebase.com" + result['id'],
            'title': result['name'],
            'characters': props['extractor'](result)
          })

    def cast(self, irc, msg, args, channel, work_type, thing):
      """<movie|tv|play|book> <title>
      Cast <title> using information retrieved from Freebase. You must specify the type of work to be cast."""

      random.seed()
      nicks = list(irc.state.channels[channel].users)
      random.shuffle(nicks)      
      record = self._query_freebase(work_type, thing)
      if record is None:
        irc.reply('I can\'t find a %s called "%s" in Freebase!' % (work_type, thing))
      else:
        title = record['title']
        parts = record['characters']

        if len(parts) == 0:
          irc.reply('I found a %s called "%s", but there are no characters listed. %s' % (work_type, thing, record['url']))
        elif len(parts) > len(nicks):
          irc.reply('Not enough people in %s to cast "%s"' % (channel, title))
        else:
          parts.reverse()
          response = '%s presents "%s", starring ' % (channel, title)
          while len(parts) > 1:
            response += "%s as %s, " % (nicks.pop(), parts.pop())
            if len(parts) == 1:
              response += "and "
          response += "%s as %s." % (nicks.pop(), parts.pop())
          irc.reply(response.encode('utf8'), prefixNick=False)

    cast = wrap(cast, ['channeldb', 'somethingWithoutSpaces', 'text'])

Class = Cast


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
