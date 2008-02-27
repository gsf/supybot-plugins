###
# Copyright (c) 2006, James Vega
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

import re
import time

import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.schedule as schedule
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Vim(callbacks.Plugin):
    _fnUser = re.compile(r'^(?:n|i)=')
    def _ban(self, irc, nick, channel):
        try:
            hostmask = irc.state.nickToHostmask(nick)
        except KeyError:
            return
        (nick, user, host) = ircutils.splitHostmask(hostmask)
        user = self._fnUser.sub('*', user)
        banmask = ircutils.joinHostmask('*', user, host)
        if ircutils.hostmaskPatternEqual(banmask, irc.prefix):
            return
        irc.queueMsg(ircmsgs.ban(channel, banmask))
        irc.queueMsg(ircmsgs.kick(channel, nick))
        expiry = self.registryValue('autokban.timeout', channel)
        if expiry > 0:
            expiry += time.time()
            def f():
                if channel in irc.state.channels and \
                   banmask in irc.state.channels[channel].bans:
                    irc.queueMsg(ircmsgs.unban(channel, banmask))
            schedule.addEvent(f, expiry)

    def doPrivmsg(self, irc, msg):
        chan = msg.args[0]
        if irc.isChannel(chan):
            if self.registryValue('autokban', chan) and \
               irc.state.channels[chan].isOp(irc.nick):
                if self.registryValue('autokban.phrase', chan) and \
                   re.search(self.registryValue('autokban.phrase', chan, re.I),
                             msg.args[1]):
                    self._ban(irc, msg.nick, chan)
        return msg


Class = Vim


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
