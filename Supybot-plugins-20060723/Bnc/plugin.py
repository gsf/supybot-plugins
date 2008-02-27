###
# Copyright (c) 2005, Ali Afshar
#
# Almost identical to the ChannelLogger plugin
# (c) J Fincher
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
import supybot.ircmsgs as ircmsgs

class Bnc(callbacks.Plugin):
    noIgnore = True
    def __init__(self, irc):
        self.__parent = super(Bnc, self)
        self.__parent.__init__(irc)
        self.targets = []

    def bounce(self, irc, msg, args, con):
        if con not in self.targets:
            self.targets.append(con)
            irc.replySuccess()
            for channel, c in irc.state.channels.iteritems():
                self.doBounce(irc, channel, channel,
                command='bounce', extra='bouncing',
                nick=irc.nick, topic=c.topic, users=c.users, modes=c.modes,
                ops=c.ops)
        else:
            irc.reply('Already bouncing you.')
    bounce = wrap(bounce, ['sshdSource'])

    def unbounce(self, irc, msg, args, con):
        if con in self.targets:
            self.targets.remove(con)
            irc.replySuccess()
        else:
            irc.reply('You are not being bounced')
    unbounce = wrap(unbounce, ['sshdSource'])

    def msg(self, irc, msg, args, con, channel, text):
        m = ircmsgs.privmsg(channel, text)
        irc.sendMsg(m)
    msg = wrap(msg, ['sshdSource', 'channel', 'text'])

    def pmsg(self, irc, msg, args, con, nick, text):
        m = ircmsgs.privmsg(nick, text)
        irc.sendMsg(m)
    pmsg = wrap(pmsg, ['sshdSource', 'nick', 'text'])

    def names(self, irc, msg, args, channel):
        if channel in irc.state.channels:
            c = irc.state.channels[channel]
            for u in c.users:
                irc.reply('%s' % u)
        else:
            irc.reply('I am not on that channel')
    names = wrap(names, ['channel'])

    def do401(self, irc, msg):
        self.log.warning('Nick not found %s', msg.command)

    def normalizeChannel(self, irc, channel):
        return ircutils.toLower(channel)

    def doLog(self, irc, channel, s, *args, **kw):
        channel = self.normalizeChannel(irc, channel)
        s = format(s, *args)
        for t in self.targets:
            t.sendReply(s.strip(), source='bnc', inreply=channel, **kw)

    def doPrivmsg(self, irc, msg):
        if not msg.fromSshd:
            (recipients, text) = msg.args
            for channel in recipients.split(','):
                nick = msg.nick or irc.nick
                command = 'privmsg'
                importance = 3
                if ircutils.isChannel(channel):
                    importance = 2
                if ircmsgs.isAction(msg):
                    command = 'action'
                    text = ircmsgs.unAction(msg)
                self.doBounce(irc, text, channel, command=command, nick=nick,
                importance=importance)

    def doBounce(self, irc, s, channel, **kw):
        channel = self.normalizeChannel(irc, channel)
        s = ircutils.stripFormatting(s)
        for t in self.targets:
            if ircutils.isChannel(channel):
                inreply = channel
            else:
                inreply = kw['nick']
            t.sendReply(s.strip(), source='bnc', inreply=inreply, **kw)

    def doNotice(self, irc, msg):
        (recipients, text) = msg.args
        for channel in recipients.split(','):
            self.doBounce(irc, text, channel, command='NOTICE', nick=msg.nick)

    def doNick(self, irc, msg):
        oldNick = msg.nick
        newNick = msg.args[0]
        for (channel, c) in irc.state.channels.iteritems():
            if newNick in c.users:
                self.doBounce(irc, newNick, channel, command='nick',
                hm=msg.prefix, nick=newNick, evalue=oldNick, importance=1)

    def doJoin(self, irc, msg):
        for channel in msg.args[0].split(','):
            self.doBounce(irc, msg.nick, channel, hm=msg.prefix,
            command='join', evalue=channel, importance=1)

    def doKick(self, irc, msg):
        if len(msg.args) == 3:
            (channel, target, kickmsg) = msg.args
        else:
            (channel, target) = msg.args
            kickmsg = ''
        self.doBounce(irc, target, channel, nick=msg.nick, evalue=msg.nick,
        extra=kickmsg, command='kick', importance=1)
        
    def doPart(self, irc, msg):
        for channel in msg.args[0].split(','):
            self.doBounce(irc, msg.nick, channel, command='part',
            hm=msg.prefix, nick=msg.nick, importance=1)

    def doMode(self, irc, msg):
        channel = msg.args[0]
        if irc.isChannel(channel) and msg.args[1:]:
            s = ' '.join([msg.args[1], ' '.join(msg.args[2:])])
            self.doBounce(irc, s, channel, command='mode',
            nick=msg.nick, extra=msg.nick, importance=1)

    def doTopic(self, irc, msg):
        if len(msg.args) == 1:
            return # It's an empty TOPIC just to get the current topic.
        channel = msg.args[0]
        self.doBounce(irc, msg.args[1], channel, command='topic',
        nick=msg.nick, importance=1, topic=msg.args[1])

    def doQuit(self, irc, msg):
        for (channel, chan) in self.lastStates[irc].channels.iteritems():
            if msg.nick in chan.users:
                self.doBounce(irc, msg.nick, command='quit', hm=msg.prefix,
                nick=msg.nick, importance=1)
               

    def outFilter(self, irc, msg):
        # Gotta catch my own messages *somehow* :)
        # Let's try this little trick...
        if msg.command in ('PRIVMSG', 'NOTICE'):
            # Other messages should be sent back to us.
            m = ircmsgs.IrcMsg(msg=msg, prefix=irc.prefix)
            self(irc, m)
        return msg



Class = Bnc


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
