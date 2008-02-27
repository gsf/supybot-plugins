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

# Supybot imports
import supybot.ircdb as ircdb
import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

# Twisted imports
from twisted.protocols import basic
import twisted.internet.reactor as reactor
import twisted.internet.protocol as protocol

# System imports
import sys
import socket
import struct

# Carriage return characters
CR = chr(015)
NL = chr(012)
LF = NL

# aspn cookbook
def numToDottedQuad(n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack('>L',n))

# Plugin
class Dcc(callbacks.Plugin):
    """ A plugin to allow users to connect with Dcc.
    
    To use, load the plugin, and initiate a dcc request. There are no
    configuration variables, but to control which users connect, use the Dcc
    capability."""
    def __init__(self, irc):
        callbacks.Plugin.__init__(self, irc)
        self.irc = irc
        self.factory = SupyDccFactory(self)
        self.hostmasks = {}
        self.connections = {}

    def outFilter(self, irc, msg):
        """ Checks messages for those sent via Dcc and routes them. """
        if msg.inReplyTo:
            if msg.inReplyTo.fromDcc:
                # a dcc message
                con = msg.inReplyTo.fromDcc
                # send the reply via dcc, and return None
                con.sendReply(msg.args[1])
                return None
            else:
                # otherwise pass the message on
                return msg
        else:
            # otherwise pass the message on
            return msg

    def exit(self, irc, msg, args):
        """[takes no arguments]
        
        Exit a Dcc session. This command can only be called from Dcc, and not
        from standard IRC
        """
        if msg.fromDcc:
            connection = msg.fromDcc
            connection.close()
        else:
            irc.reply('"exit" may only be called from DCC.')
    exit = wrap(exit, [])

    def die(self):
        """ Shut down all the connections. """
        for hostport in self.connections:
            self.connections[hostport].close()
        self.connections = {}
        self.hostmasks = {}

    def _connectDcc(self, host, port):
        """ Connect to a DCC connection. """
        reactor.connectTCP(host, port, self.factory)

    def _dccRequest(self, hostmask, command):
        """ Handle a DCC request. """
        args = command.split()
        if args[1].startswith('CHAT'):
            try:
                port = int(args.pop())
                host = numToDottedQuad(int(args.pop()))
                self._dccChatRequest(hostmask, host, port)
            except ValueError:
                self.log.debug('Bad DCC request: %s', command.strip())

    def _dccChatRequest(self, hostmask, host, port):
        """ Handle a Dcc chat request. """
        if self._isDccCapable(hostmask):
            self.hostmasks[(host, port)] = hostmask
            self._connectDcc(host, port)
        else:
            self.log.debug('Failed connection attempt, incapable %s.',
                            hostmask)

    def _isDccCapable(self, hostmask):
        """ Check if the user is DCC capable. """
        return ircdb.checkCapability(hostmask, 'Dcc')

    def _lineReceived(self, connection, host, port, line):
        """ Handle a line received over DCC. """
        if (host, port) in self.hostmasks:
            hm = self.hostmasks[(host, port)]
            cmd = line.strip()
            to = self.irc.nick
            m =  ircmsgs.privmsg(to, cmd, hm)
            m.tag('fromDcc', connection)
            self.irc.feedMsg(m)

    def doPrivmsg(self, irc, msg):
        """ Check whether a privmsg is a DCC request. """
        text = msg.args[1].strip('\x01')
        if text.startswith('DCC'):
            self._dccRequest(msg.prefix, text)


class SupyDccChat(basic.LineReceiver):
    """ Basic line protocol """    

    def __init__(self, cb):
        self.cb = cb
        self.delimiter = CR + NL
        self.rbuffer = ""

    def connectionMade(self):
        """ Called when the connection has been made. """
        t, self.host, self.port = self.transport.getPeer()
        self.cb.connections[(self.host, self.port)] = self
        self.transport.write('Connected to Supybot Dcc interface.\r\n')

    def connectionLost(self, reason):
        """ Called when the connection has been lost, or closed. """
        del self.cb.connections[(self.host, self.port)]
        del self.cb.hostmasks[(self.host, self.port)]

    def dataReceived(self, data):
        """ Called when data is received. """
        self.rbuffer = self.rbuffer + data
        lines = self.rbuffer.split(LF)
        # Put the (possibly empty) element after the last LF back in the
        # buffer
        self.rbuffer = lines.pop()
        for line in lines:
            if line[-1] == CR:
                line = line[:-1]
            self.lineReceived(line)

    def lineReceived(self, line):
        """ Called on the receipt of each line. """
        self.cb._lineReceived(self, self.host, self.port, line)

    def sendReply(self, reply):
        """ Send a reply. """
        self.transport.write('%s\r\n' % reply)

    def close(self):
        self.sendReply('* Closing connection down.')
        self.transport.loseConnection()

class SupyDccFactory(protocol.ClientFactory):
    """ Client connector factory for Dcc """

    def __init__(self, cb):
        self.cb = cb
        self.protocol = SupyDccChat

    def buildProtocol(self, addr):
        """ Called to create an instance of the protocol. """
        p = self.protocol(self.cb)
        p.factory = self
        return p

Class = Dcc


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
