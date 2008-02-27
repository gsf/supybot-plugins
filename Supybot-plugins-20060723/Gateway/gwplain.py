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
from twisted.protocols import basic
from twisted.internet import protocol, reactor


from gwbase import BasePlugin

class SBPlainProtocol(basic.LineReceiver):
	def connectionMade(self):
		self.cb.authorised(self.user)
		self.cb._connections.append(self.user)
		
	
	def lineReceived(self, line):
		if len(line):
			self.factory.cb.cb.receivedCommand(line, self.user)


class PlainUser:
	def __init__(self, cb, p, addr):
		self.cb = cb
		self.p = p
		self.hostmask = self.cb.cb.buildAnonymousHostmask(self.cb.PROTOCOL,
			addr.host)
	
	def sendReply(self, reply, inreply):
		self.p.transport.write('%s\r\n' % reply)
		
	def close(self):
		self.p.transport.loseConnection()
		self.cb._connections.remove(self)

class PlainGW(BasePlugin):
	PROTOCOL = "plain"
	USESSL = False
	PORTALISE = False
	DEFAUL_PORT = 9021
	CONFIG_EXTRA = []

	class FactoryClass(protocol.ServerFactory):
		protocol = SBPlainProtocol

		def buildProtocol(self, addr):
			p = protocol.ServerFactory.buildProtocol(self, addr)
			p.user = PlainUser(self.cb, p, addr)
			return p

			
