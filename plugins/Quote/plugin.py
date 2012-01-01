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
import sys

class Ranking(object):
  
  def __init__(self, *args):
    self.data = {}
      
  def sorted_data(self):
    result = sorted(self.data.iteritems())
    return sorted(result, key=lambda c:c[1], reverse=True)
    
  def increment(self, key):
    if self.data.has_key(key):
      self.data[key] += 1
    else:
      self.data[key] = 1
  
  def set(self, key, value):
    self.data[key] = value
    
  def items_at(self, value):
    return [c for c in self.sorted_data() if c[1] == value]

  def keys_at(self, value):
    return map(lambda c: c[0], self.items_at(value))
    
  def rank(self,key):
    value = self.data[key]

    sd = self.sorted_data()
    unique_values = sorted(set(map(lambda c: c[1], sd)), reverse=True)
    
    standard = len([c for c in sd if c[1] > value]) + 1
    dense = unique_values.index(value) + 1
    result = { 
      'nick' : key,
      'ordinal' : [sd.index(c) for c in sd if c[0] == key][0]+1, 
      'competition' : standard, 
      'dense' : dense, 
      'value' : value,
      'entries' : len(sd), 
      'ranks' : len(unique_values),
      'tied_with' : [k for k in self.keys_at(value) if k != key]
    }
    result['noun'] = 'citation'
    if result['value'] > 1:
      result['noun'] = 'citations'
    return result

class Quote(plugins.ChannelIdDatabasePlugin):

    def cited(self, irc, msg, args, channel, opts, nick):
      """[<channel>] [--matching <regexp>] [<nick>]
      
      Finds out how many times <nick> is cited in <channel>'s quote database. If <nick> is not
      supplied, returns the top 5 cited users and the calling user's ranking. If --matching is
      supplied, only quotes matching <regexp> are considered."""
      quote_filter = None
      selector = lambda x: True
      for (opt,arg) in opts:
        if opt == 'matching':
          quote_filter = '/%s/' % arg.pattern
          selector = lambda x, arg=arg: arg.search(x.text)
                    
      cites = {}
      pattern = re.compile("<\s*(\S.+\S)\s*>")

      r = Ranking()
      
      for quote in self.db.select(channel, selector):
        match = pattern.match(quote.text)
        if match != None:
          person = match.group(1)
          r.increment(person)
      
      rank_requested = False
      response = ''
      if quote_filter:
        response += 'For quotes matching %s: ' % quote_filter
      
      if nick == None:
        top_cites = []
        for cite in r.sorted_data()[0:5]:
          top_cites.append("%s (%d)" % cite)
        response += "Top %d quoted users in %s: %s." % (len(top_cites), channel, '; '.join(top_cites))
        user_cite_prefix = " You (%s) are" % msg.nick
        nick = msg.nick
      elif re.match("^[0-9]+$",nick):
        rank_requested = True
        user_cite_prefix = ""
      else:
        user_cite_prefix = "%s is" % nick

      try:
        if rank_requested:
          try:
            response = ""
            requested_rank = int(nick)
            new_nick = r.sorted_data()[requested_rank-1][0]
            d = r.rank(new_nick)
            d['channel'] = channel
            if d['competition'] != requested_rank:
              response = "Due to a tie, %d is not a valid rank. " % requested_rank
            d['tied_with'].append(new_nick)
            if len(d['tied_with']) == 1:
              phrase = "%(nick)s is ranked number %(competition)d out of %(entries)d with %(value)d %(noun)s."
            else:
              d['user_list'] = " and " + d['tied_with'].pop()
              if len(d['tied_with']) == 1:
                d['user_list'] = d['tied_with'][0] + d['user_list']
              else:
                d['user_list'] = ', '.join(d['tied_with']) + ", " + d['user_list']
              phrase = "%(user_list)s are tied for number %(competition)d out of %(entries)d with %(value)d %(noun)s."
            response += phrase %d
          except IndexError:
            response = "There are no users ranked at #%s in the %s quote database." % (nick, channel)
        else:
          d = r.rank(nick)

          d['prefix'] = user_cite_prefix
          d['tie_count'] = len(d['tied_with'])
          d['channel'] = channel
          
          phrase = "%(prefix)s ranked number %(competition)d out of %(entries)d with %(value)d %(noun)s."
          if len(d['tied_with']) > 1:
            phrase = "%(prefix)s tied with %(tie_count)d other users for number %(competition)d out of %(entries)d with %(value)d %(noun)s."
          elif len(d['tied_with']) == 1:
            phrase = "%(prefix)s tied with %(tie_count)d other user for number %(competition)d out of %(entries)d with %(value)d %(noun)s."
          response += phrase % d
      except KeyError:
        if len(response) == 0:
          response = "%s has no quotes in the %s quote database." % (nick, channel)

      irc.reply(response.encode('utf-8'), prefixNick=False)
      
    cited = wrap(cited, ['channeldb', getopts({'matching': 'regexpMatcher'}), optional('nick')])
    
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
