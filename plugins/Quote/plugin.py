###
# Copyright (c) 2005, Daniel DiPaolo
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

from supybot.commands import *
import supybot.plugins as plugins
import re
from ranking import Ranking

class Quote(plugins.ChannelIdDatabasePlugin):

    def cited(self, irc, msg, args, channel, nick):
      """[<channel>] [<nick>]
      
      Finds out how many times <nick> is cited in <channel>'s quote database. If <nick> is not
      supplied, returns the top 5 cited users and the calling user's ranking."""
      cites = {}
      pattern = re.compile("<\s*(\S.+\S)\s*>")

      r = Ranking()
      
      for quote in self.db.select(channel, lambda x: True):
        match = pattern.match(quote.text)
        if match != None:
          person = match.group(1)
          r.increment(person)
      
      response = ''
      
      if nick == None:
        top_cites = []
        for cite in r.sorted_data()[0:5]:
          top_cites.append("%s (%d)" % cite)
        response += "Top %d quoted users in %s: %s." % (len(top_cites), channel, '; '.join(top_cites))
        user_cite_prefix = " You (%s) are" % msg.nick
        nick = msg.nick
      else:
        user_cite_prefix = "%s is" % nick

      try:
        d = r.rank(nick)

        d['prefix'] = user_cite_prefix
        d['tie_count'] = len(d['tied_with'])
        d['channel'] = channel
        d['noun'] = 'citation'
        if d['value'] > 1:
          d['noun'] = 'citations'
          
        phrase = "%(prefix)s ranked number %(competition)d out of %(entries)d with %(value)d %(noun)s."
        if len(d['tied_with']) > 1:
          phrase = "%(prefix)s tied with %(tie_count)d other users for #%(competition)d out of %(entries)d with %(value)d %(noun)s."
        elif len(d['tied_with']) == 1:
          phrase = "%(prefix)s tied with %(tie_count)d other user for #%(competition)d out of %(entries)d with %(value)d %(noun)s."
        response += phrase % d
      except KeyError:
        if len(response) == 0:
          response = "%s has no quotes in the %s quote database." % (nick, channel)

      irc.reply(response.encode('utf-8'), prefixNick=False)
      
    cited = wrap(cited, ['channeldb', optional('nick')])
    
    def random(self, irc, msg, args, channel):
        """[<channel>]

        Returns a random quote from <channel>.  <channel> is only necessary if
        the message isn't sent in the channel itself.
        """
        quote = self.db.random(channel)
        if quote:
            irc.reply(self.showRecord(quote))
        else:
            irc.error('I have no quotes in my database for %s.' % channel)
    random = wrap(random, ['channeldb'])

    def raw(self, irc, msg, args, channel, id):
      """[<channel>] [<id>]
      
      Returns the quote (identified by <id>) from <channel>, with attribution 
      and metadata stripped. <channel> is only necessary if the message isn't 
      sent in the channel itself. If <id> isn't specified, a random quote is 
      returned.
      """
      if id is None:
        quote = self.db.random(channel)
      else:
        quote = self.db.get(channel,id)
        
      if quote:
        irc.reply(re.sub("^<.+?>\s*",'',quote.text))
      else:
        irc.error('I have no quotes in my database for %s.' % channel)
    raw = wrap(raw, ['channeldb', optional('id')])
    
Class = Quote

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
