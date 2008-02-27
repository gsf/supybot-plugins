###
# Copyright (c) 2004-2005, Jeremiah Fincher
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
import supybot.ircutils as ircutils
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Tail', True)

class ValidChannelOrNick(registry.String):
    """Value must be a valid channel or a valid nick."""
    def setValue(self, v):
        if not (ircutils.isNick(v) or ircutils.isChannel(v)):
            self.error()
        registry.String.setValue(self, v)

class Targets(registry.SpaceSeparatedListOfStrings):
    Value = ValidChannelOrNick

Tail = conf.registerPlugin('Tail')
conf.registerGlobalValue(Tail, 'targets',
    Targets([], """Determines what targets will be messaged with lines from the
    files being tailed."""))
conf.registerGlobalValue(Tail, 'bold',
    registry.Boolean(False, """Determines whether the bot will bold the filename
    in tail lines announced to the channel."""))
conf.registerGlobalValue(Tail, 'files',
    registry.SpaceSeparatedSetOfStrings([], """Determines what files the bot
    will tail to its targets."""))
conf.registerGlobalValue(Tail, 'notice',
    registry.Boolean(False, """Determines whether the bot will send its tail
    messages to the targets via NOTICEs rather than PRIVMSGs."""))
conf.registerGlobalValue(Tail, 'period',
    registry.PositiveInteger(60, """Determines how often the bot will check
    the files that are being tailed.  The number is in seconds.  This plugin
    must be reloaded for changes to this period to take effect."""))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
