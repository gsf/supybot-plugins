###
# Copyright (c) 2005, Jeremiah Fincher
# Copyright (c) 2006, Jon Phillips
# Copyright (c) 2006, Creative Commons
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
    conf.registerPlugin('Mailbox', True)


Mailbox = conf.registerPlugin('Mailbox')
conf.registerGlobalValue(Mailbox, 'server',
    registry.String('', """Determines what POP3 server to connect to in order
    to check for email."""))
conf.registerGlobalValue(Mailbox, 'user',
    registry.String('', """Determines what username to give to the POP3 server
    when connecting."""))
conf.registerGlobalValue(Mailbox, 'password',
    registry.String('', """Determines what password to give to the POP3 server
    when connecting.""", private=True))
conf.registerGlobalValue(Mailbox, 'period',
    registry.PositiveInteger(180, """Determines how often the bot will check
    the POP3 server for new messages to announce."""))
conf.registerGlobalValue(Mailbox, 'prefix',
    registry.String('WARNING: ', """Determines what prefix will be used before
    announcing emails."""))
conf.registerGlobalValue(Mailbox, 'fancystyle',
    registry.Boolean(False,
    """Use non-standard mIRC styling (red and bold) of email message."""))
conf.registerGlobalValue(Mailbox, 'fancyprefix',
    registry.Boolean(False, 
    """Use non-standard mIRC styling (bold) of prefix."""))
conf.registerChannelValue(Mailbox, 'limit',
    registry.PositiveInteger(1, """Determines the maximum number of messages
    that will be sent for a given email."""))
conf.registerGlobalValue(Mailbox, 'defaultChannels',
    conf.SpaceSeparatedSetOfChannels([], """Determines to which channels the
    bot will send messages that do not have a subject line consisting entirely
    of channels."""))


# vim:set shiftwidth=4 softtabstop=8 expandtab textwidth=78
