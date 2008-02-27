###
# Copyright (c) 2005, Jeremiah Fincher
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
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('ChannelRelay', True)

class ValidChannelOrNothing(conf.ValidChannel):
    """Value must be either a valid IRC channel or the empty string."""
    def setValue(self, v):
        try:
            conf.ValidChannel.setValue(self, v)
        except registry.InvalidRegistryValue:
            registry.Value.setValue(self, '')

ChannelRelay = conf.registerPlugin('ChannelRelay')
conf.registerGlobalValue(ChannelRelay, 'source',
    ValidChannelOrNothing('', """Determines the channel that the bot will look
    for messages to relay from.  Messages matching
    supybot.plugins.ChannelRelay.regexp will be relayed to the target channel
    specified by supybot.plugins.ChannelRelay.target."""))
conf.registerGlobalValue(ChannelRelay, 'target',
    ValidChannelOrNothing('', """Determines the channel that the bot will send
    messages from the other channel.  Messages matching
    supybot.plugins.ChannelRelay.regexp will be relayed to this channel from
    the source channel."""))
conf.registerGlobalValue(ChannelRelay, 'regexp',
    registry.Regexp(None, """Determines what regular expression
    should be matched against messages to determine whether they should be
    relayed from the source channel to the target channel.  By default, the
    value is m/./, which means that all non-empty messages will be
    relayed."""))
if ChannelRelay.regexp() is None:
    ChannelRelay.regexp.set('m/./')
conf.registerGlobalValue(ChannelRelay, 'fancy',
    registry.Boolean(True, """Determines whether the bot should relay the
    messages in fancy form (i.e., including the nick of the sender of the
    messages) or non-fancy form (i.e., without the nick of the sender of the
    messages)."""))
conf.registerGlobalValue(ChannelRelay, 'prefix',
    registry.String('', """Determines what prefix should be prepended to the
    relayed messages."""))

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
