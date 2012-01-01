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

from random import choice
import re
import time

PRIVATE_COMMANDS = ['get','remove']
SARCASTIC = { 'love' : '"hate"', 'loves' : '"hates"', 'hate' : '"love"', 'hates' : '"loves"' }
OPPOSITES = { 'love' : 'hate', 'hate' : 'love' }

class LoveHate(callbacks.Plugin):
    class DB(plugins.DbiChannelDB):
        class DB(dbi.DB):
            class Record(dbi.Record):
                __fields__ = [
                    'emotion',
                    'at',
                    'by',
                    'text'
                ]
            def add(self, emotion, at, by, text, **kwargs):
                record = self.Record(emotion=emotion, at=at, by=by, text=text, **kwargs)
                return super(self.__class__, self).add(record)
                
    def __init__(self, irc):
        self.__parent = super(LoveHate, self)
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
        
    def _feels(self, channel, user, thing):
        check = lambda r: (r.by == user and r.text.lower() == thing.lower())
        result = self._select(channel, [check])
        try:
            return result.next().emotion
        except StopIteration:
            return None
        
    def _lovehate(self, irc, msg, args, channel, emotion, thing):
        at = time.time()
        if thing is not None:
            previous = self._feels(channel, msg.nick, thing)
            if previous == None:
                id = self.db.add(channel, emotion, at, msg.nick, thing)
                irc.replySuccess('%s %ss %s.' % (msg.nick, emotion, thing))
            else:
                irc.reply('But %s already %ss %s!' % (msg.nick, previous, thing))

    def _counts(self, channel):
      result = {}
      for record in self._select(channel, [lambda x: True]):
        if not result.has_key(record.by):
          result[record.by] = { 'love' : 0, 'hate' : 0 }
        result[record.by][record.emotion] += 1
      return result
      
    def _top(self, irc, msg, args, channel, emotion):
      counts = self._counts(channel)
      result = sorted(counts.iteritems(), key=lambda x: x[1][emotion], reverse=True)[0:5]
      response_list = []
      for r in result:
        response_list.append("%s (%d)" % (r[0], r[1][emotion]))
      response = "Top %srs: %s" % (emotion, '; '.join(response_list))
      irc.reply(response)      
      
    def lovers(self, irc, msg, args, channel):
      self._top(irc, msg, args, channel, 'love')
    lovers = wrap(lovers, ['channeldb'])
      
    def haters(self, irc, msg, args, channel):
      self._top(irc, msg, args, channel, 'hate')
    haters = wrap(haters, ['channeldb'])

    def love(self, irc, msg, args, channel, thing):
        """<thing>
        Declare your love for <thing>"""
        self._lovehate(irc, msg, args, channel, 'love', thing)
    love = wrap(love, ['channeldb', 'text'])

    def hate(self, irc, msg, args, channel, thing):
        """<thing>
        Declare your hate for <thing>"""
        self._lovehate(irc, msg, args, channel, 'hate', thing)
    hate = wrap(hate, ['channeldb', 'text'])

    sarcasticlove = hate

    def dontcare(self, irc, msg, args, channel, thing):
        """<thing>
        Declare that you no longer care one way or the other about <thing>"""
        try:
            record = self._select(channel, [lambda r: r.by == msg.nick and r.text.lower() == thing.lower()]).next()
            self.db.remove(channel, record.id)
            irc.replySuccess('%s no longer %ss %s.' % (msg.nick, record.emotion, thing))
        except StopIteration:
            irc.reply("I have no record of %s's loving or hating %s" % (msg.nick, thing))
    dontcare = wrap(dontcare, ['channeldb', 'text'])

    def _find_stuff_out(self, channel, predicate, emotion, extractor = lambda r: r):
        predicates = [predicate]
        if emotion != None:
            predicates.append(lambda r: r.emotion == emotion)
        enum = self._select(channel, predicates)
        results = {'love':[], 'hate':[]}
        try:
            while True:
                r = enum.next()
                results[r.emotion].append(extractor(r))
        except StopIteration:
            pass
        return results
    
    def _whocares(self, irc, msg, args, channel, emotion, opts, thing):
        if ('sarcasm' in dict(opts)) and (emotion != None):
          emo_key = OPPOSITES[emotion]
        else:
          emo_key = emotion
        results = self._find_stuff_out(channel, lambda r: r.text.lower() == thing.lower(), emo_key, lambda r: r.by)
        replied = False
        for key in ('love','hate'):
            if len(results[key]) > 0:
                if len(results[key]) > 1:
                    users = ', '.join(results[key][0:-1]) + ' and ' + results[key][-1]
                    verb = key
                else:
                    users = ' and '.join(results[key])
                    verb = key + 's'
                if 'sarcasm' in dict(opts):
                  verb = SARCASTIC[verb]
                irc.reply(' '.join((users, verb, thing)), prefixNick=False)
                replied = True
                
        if not replied:
            if emotion == None:
                irc.reply("I can't find anyone who loves or hates %s." % (thing))
            else:
                irc.reply("I can't find anyone who %ss %s." % (emotion, thing))
                
                
    def whocares(self, irc, msg, args, channel, opts, thing):
        """[<channel>] <thing>
        Find out who cares about <thing>"""
        self._whocares(irc, msg, args, channel, None, opts, thing)
    whocares = wrap(whocares, ['channeldb',getopts({'sarcasm':''}),'text'])

    def wholoves(self, irc, msg, args, channel, opts, thing):
        """[<channel>] <thing>
        Find out who loves <thing>"""
        self._whocares(irc, msg, args, channel, 'love', opts, thing)
    wholoves = wrap(wholoves, ['channeldb',getopts({'sarcasm':''}),'text'])

    def whohates(self, irc, msg, args, channel, opts, thing):
        """[<channel>] <thing>
        Find out who hates <thing>"""
        self._whocares(irc, msg, args, channel, 'hate', opts, thing)
    whohates = wrap(whohates, ['channeldb',getopts({'sarcasm':''}),'text'])
    
    def _caresabout(self, irc, msg, args, channel, user, opts, emotion):
        if user is None:
            user = msg.nick
        if ('sarcasm' in dict(opts)) and (emotion != None):
          emo_key = OPPOSITES[emotion]
        else:
          emo_key = emotion
        results = self._find_stuff_out(channel, lambda r: r.by == user, emo_key, lambda r: r.text)
        replied = False
        for key in ('love','hate'):
            if len(results[key]) > 0:
                verb = key + 's'
                if 'sarcasm' in dict(opts):
                  verb = SARCASTIC[verb]
                if len(results[key]) > 1:
                    things = '; '.join(results[key][0:-1]) + '; and ' + results[key][-1]
                else:
                    things = ' and '.join(results[key])
                irc.reply(' '.join((user, verb, things)), prefixNick=False)
                replied = True

        if not replied:
            if emotion == None:
                irc.reply("%s doesn't seem to care about anything." % (user))
            else:
                irc.reply("%s doesn't seem to %s anything." % (user, emotion))
            
    def caresabout(self, irc, msg, args, channel, opts, user):
        """[<channel>] [<user>]
        Find out what <user> cares about"""
        self._caresabout(irc, msg, args, channel, user, opts, None)
    caresabout = wrap(caresabout, ['channeldb',getopts({'sarcasm':''}),optional('nick')])

    def loves(self, irc, msg, args, channel, opts, user):
        """[<channel>] [<user>]
        Find out what <user> loves"""
        self._caresabout(irc, msg, args, channel, user, opts, 'love')
    loves = wrap(loves, ['channeldb',getopts({'sarcasm':''}),optional('nick')])

    def hates(self, irc, msg, args, channel, opts, user):
        """[<channel>] [<user>]
        Find out what <user> hates"""
        self._caresabout(irc, msg, args, channel, user, opts, 'hate')
    hates = wrap(hates, ['channeldb',getopts({'sarcasm':''}),optional('nick')])

    def random(self, irc, msg, args, channel, emotion):
        """[love|hate]
        Get some random love (or hate)"""
        if emotion == None:
            predicates = [lambda r: True]
        else:
            predicates = [lambda r: r.emotion == emotion]
        records = self._select(channel, predicates)
        L = list(records)
        try:
            record = choice(L)
        except IndexError:
            irc.reply("I can't find anyone who loves or hates anything.")
        else:
            irc.reply('%s %ss %s' % (record.by, record.emotion, record.text))
    random = wrap(random, ['channeldb',optional(("literal", ("love","hate")))])
    
    def get(self, irc, msg, args, channel, id):
        if id == None:
            records = self.db.select(channel, lambda r: True)
            responses = []
            for record in records:
                responses.append('%s: %s %s %s' % (record.id, record.by, record.emotion, record.text))
            irc.reply(' ; '.join(responses))
        else:
            record = self.db.get(channel, id)
            irc.reply('%s: %s %s %s' % (record.id, record.by, record.emotion, record.text))
    get = wrap(get, [('checkCapability','admin'), 'channeldb', optional('id')])
    
    def remove(self, irc, msg, args, channel, id):
        if id == None:
            irc.reply('No id specified')
        try:
            self.db.remove(channel, id)
            irc.replySuccess()
        except:
            irc.replyError()
    remove = wrap(remove, [('checkCapability','admin'), 'channeldb', 'id'])
        
    def listCommands(self, pluginCommands=[]):
        L = self.__parent.listCommands(pluginCommands)
        for cmd in PRIVATE_COMMANDS:
            L.remove(cmd)
        return L
        
Class = LoveHate


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
