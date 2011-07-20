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
import supybot.dbi as dbi

from random import randint
import re
import time

class Cast(callbacks.Plugin):
    class DB(plugins.DbiChannelDB):
        class DB(dbi.DB):
            class Record(dbi.Record):
                __fields__ = [
                    'play',
                    'cast'
                ]
            def add(self, play, cast, **kwargs):
                record = self.Record(play=play, cast=cast, **kwargs)
                return super(self.__class__, self).add(record)
                
    def __init__(self, irc):
        self.__parent = super(Cast, self)
        self.__parent.__init__(irc)
        self.db = plugins.DB(self.name(), {'flat': self.DB})()
        
    def die(self):
        self.db.close()
        self.__parent.die()
        
    def _select(self, channel, predicates):
        def p(record):
            for predicate in predicates:
                if not predicate(record):
                    return False
            return True
        return self.db.select(channel, p)
        
    def _find(self, channel, play):
      check = lambda r: (r.play.lower() == play.lower())
      result = self._select(channel, [check])
      try:
        record = result.next()
        return record
      except StopIteration:
        return None
    
    def add(self, irc, msg, args, channel, play, cast):
      """<play> <cast> -- Add <play> to the database, with parts specified by <cast> (separated by semicolons)"""
      previous = self._find(channel, play)
      if previous is not None:
        irc.reply('"%s" already exists.' % (play))
      else:
        id = self.db.add(channel, play, cast)
        irc.replySuccess('"%s" added.' % (play))
    add = wrap(add, ['channeldb','something','something'])

    def remove(self, irc, msg, args, channel, play):
      """<play> -- Remove <play> from the database"""
      if id == None:
        irc.reply('No id specified')
      try:
        record = self._find(channel, play)
        if record is not None:
          self.db.remove(channel, record.id)
          irc.replySuccess()
        else:
          irc.reply('"%s" not found' % play)
      except:
          irc.replyError()
    remove = wrap(remove, [('checkCapability','admin'), 'channeldb', 'something'])

    def list(self, irc, msg, args, channel):
      """List plays that I can cast"""
      records = self._select(channel, [lambda x: True])
      titles = ['"%s"' % record.play for record in records]
      titles.sort()
      irc.reply(', '.join(titles))
    list = wrap(list, ['channeldb'])
    
    def cast(self, irc, msg, args, channel, play):
      """[<play>] -- Cast <play> from the current channel participants."""
      nicks = list(irc.state.channels[channel].users)
      nicks.sort(lambda a,b: randint(-1,1))
      
      if play is None:
        record = self.db.random(channel)
        play = record.play
      else:
        record = self._find(channel, play)
        
      if record is not None:
        parts = re.split(r'\s*;\s*',record.cast)
        if len(parts) > len(nicks):
          irc.reply('Not enough people in %s to cast "%s"' % (channel, play))
        else:
          parts.reverse()
          response = '%s presents "%s", starring ' % (channel, play)
          while len(parts) > 1:
            response += "%s as %s, " % (nicks.pop(), parts.pop())
            if len(parts) == 1:
              response += "and "
          response += "%s as %s." % (nicks.pop(), parts.pop())
          irc.reply(response.encode('utf8'), prefixNick=False)
      else:
        irc.reply('I don\'t know "%s"!' % play)
    cast = wrap(cast, ['channeldb', optional('something')])
    
Class = Cast


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
