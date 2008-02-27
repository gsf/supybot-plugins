###
# Copyright (c) 2005, James Vega
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
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class IgnoreFormatting(callbacks.Plugin):
    """By default, this plugin is disabled.  To enable it in a specific
    channel, use the enable command.  If you want it to be enabled globally,
    set supybot.plugins.IgnoreFormatting.enabled to True."""
    public = False
    def inFilter(self, irc, msg):
        if ircutils.isChannel(msg.args[0]):
            if self.registryValue('enabled', msg.args[0]) and \
               len(msg.args) > 1:
                s = ircutils.stripFormatting(msg.args[1])
                msg = ircmsgs.privmsg(msg.args[0], s, msg=msg)
                return msg
        return msg

    def enable(self, irc, msg, args, channel):
        """
        [<channel>]

        Enables this plugin in <channel>, thus ignoring any formatting of
        messages the bot sees.  <channel> is only necessary if the message
        isn't sent in the channel itself.
        """
        self.setRegistryValue('enabled', True, channel)
        irc.replySuccess()
    enable = wrap(enable, ['channel'])

    def disable(self, irc, msg, args, channel):
        """
        [<channel>]

        Disables this plugin in <channel>.  <channel> is only necessary if the
        message isn't sent in the channel itself.
        """
        self.setRegistryValue('enabled', False, channel)
        irc.replySuccess()
    disable = wrap(disable, ['channel'])


Class = IgnoreFormatting


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
