###
# Copyright (c) 2004, James Vega
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

from itertools import ifilter

import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Grasshoppaz(callbacks.Privmsg):
    """Add the help for "@help Grasshoppaz" here."""
    def _validLastMsg(self, irc, msg, chan):
        return msg.prefix and \
               msg.command == 'PRIVMSG' and \
               irc.isChannel(msg.args[0]) and \
               ircutils.strEqual(chan, msg.args[0])

    def _normalize(self, m):
        if ircmsgs.isAction(m):
            n = ircmsgs.prettyPrint(m).split(None, 2)
            try:
                return [' '.join(n[:2]), n[2]]
            except IndexError: # empty action
                return [' '.join(n[:2]), '\x00']
        else:
            pretty = ircmsgs.prettyPrint(m).split(None, 1)
            if len(pretty) == 1:
                pretty.append('\x00')
            return pretty

    def s(self, irc, msg, args, channel, s, r):
        """<search> <replace>

        Searches for the last message with <search> and replaces all instances
        of <search> with <replace>.
        """
        try:
            if self.registryValue('caseInsensitiveSearch', channel):
                search = re.compile(s, re.I)
            else:
                search = re.compile(s)
        except (ValueError, re.error), e:
            irc.error(str(e), Raise=True)
        iterable = ifilter(lambda m, c=channel: self._validLastMsg(irc, m, c),
                           reversed(irc.state.history))
        iterable.next() # skip the msg that invoked this command
        for msg in iterable:
            (p, m) = self._normalize(msg)
            if search.search(m):
                if self.registryValue('globalReplace', channel):
                    irc.reply(' '.join([p, search.sub(r, m)]), prefixNick=False)
                else:
                    irc.reply(' '.join([p, search.sub(r, m, 1)]),
                              prefixNick=False)
                return
        irc.error('I couldn\'t find a message with that phrase.')
    s = wrap(s, ['onlyInChannel', 'something', 'text'])

    def win(self, irc, msg, args, channel, text):
        """<phrase>

        Determines who was the first person to say <phrase>.  Useful when two
        people say similar things at the same time.
        """
        try:
            if self.registryValue('caseInsensitiveSearch', channel):
                s = re.compile(text, re.I)
            else:
                s = re.compile(text)
        except (ValueError, re.error), e:
            irc.error(str(e), Raise=True)
        iterable = ifilter(lambda m, c=channel: self._validLastMsg(irc, m, c),
                           reversed(irc.state.history))
        iterable.next() # skip the msg that invoked this command
        foundLast = False
        for msg in iterable:
            (p, m) = self._normalize(msg)
            if s.search(m):
                if foundLast:
                    if ' ' in p:
                        irc.reply('%s wins!' % p.split()[1], prefixNick=False)
                        return
                    else:
                        irc.reply('%s wins!' % p.strip('<>'), prefixNick=False)
                        return
                else:
                    foundLast = True
        if foundLast:
            s = 'I only found one message with that phrase.'
        else:
            s = 'I couldn\'t find a message with that phrase.'
        irc.error(s)
    win = wrap(win, ['onlyInChannel', 'text'])


Class = Grasshoppaz

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
