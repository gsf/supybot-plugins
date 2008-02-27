###
# Copyright (c) 2005, Ali Afshar
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
import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import twisted.internet.reactor as reactor
import twisted.internet.protocol as protocol

import os

class ExternalNotice(callbacks.Plugin):
    """Allow the supybot user to send a notice to a channel."""
    
    def __init__(self, irc):
        callbacks.Plugin.__init__(self, irc)
        self.server = SupyUDP(self)
        self.path = os.path.expanduser('~/.supybot-external-notice.%s' %
                                       self.nick)
        if os.path.exists(self.path):
            os.remove(self.path)
        self.listener = reactor.listenUNIXDatagram(self.path, self.server)
        os.chmod(self.path, 200)

    def receivedCommand(self, data):
        """Received a command over the UDP wire."""
        error = None
        commanditems = data.split()
        if len(commanditems) > 2:
            network = commanditems.pop(0)
            channel = commanditems.pop(0)
            text = ' '.join(commanditems)
            netfound = False
            for irc in world.ircs:
                if irc.network == network:
                    netfound = True
                    chanfound = False
                    for onchannel in irc.state.channels:
                        if channel == onchannel[1:]:
                            chanfound = True
                            m = ircmsgs.notice(onchannel, text)
                            irc.sendMsg(m)
                    if not chanfound:
                        error = 'Bad Channel "%s"' % channel
            if not netfound:
                error = 'Bad Network "%s"' % network
        if error:
            self.log.info('Attempted external notice: %s', error)
        else:
            self.log.info('Successful external notice')

    def die(self):
        """ Called on unload. Stop listening and remove the socket. """
        self.listener.stopListening()
        os.remove(self.path)

class SupyUDP(protocol.DatagramProtocol):
    """ A very simple datagram protocol """

    def __init__(self, cb):
        self.cb = cb

    def datagramReceived(self, data, address):
        """ Just pass the data on to the plugin. """
        self.cb.receivedCommand(data)

Class = ExternalNotice


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
