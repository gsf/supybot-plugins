###
# Copyright (c) 2004, Jeremiah Fincher
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

import supybot.conf as conf
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks

class ChannelRelay(callbacks.Privmsg):
    def shouldRelay(self, msg):
        source = self.registryValue('source')
        if source:
            assert msg.command == 'PRIVMSG'
            return msg.args[0] == source and \
                   bool(self.registryValue('regexp').search(msg.args[1]))
        else:
            return False

    def doPrivmsg(self, irc, msg):
        if self.shouldRelay(msg):
            target = self.registryValue('target')
            if target and target in irc.state.channels:
                if self.registryValue('fancy'):
                    s = ircmsgs.prettyPrint(msg)
                else:
                    s = msg.args[1]
                s = self.registryValue('prefix') + s
                irc.queueMsg(ircmsgs.privmsg(target, s))

    def do376(self, irc, msg):
        source = self.registryValue('source')
        target = self.registryValue('target')
        if source and target:
            networkGroup = conf.supybot.networks.get(irc.network)
            irc.queueMsg(networkGroup.channels.join(target))
            irc.queueMsg(networkGroup.channels.join(source))


Class = ChannelRelay

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
