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

import gwssl
import gwcred
from twisted.internet import reactor

# Base plugin class
class BasePlugin(object):
    """ Base Plugin Class """
    PORTALISE = False
    USESSL = True
    DEFAULT_PORT = 9999
    CAPABILITY = ''

    def __init__(self, cb):
        self._connections = []
	self.listener = None
        self.cb = cb
        # set regitry sruff here
        self.personalRegistryValue = lambda s: \
            self.cb.registryValue('%s.%s' % (self.PROTOCOL, s))

        self.mainRegistryValue = self.cb.registryValue
        self.log = self.cb.log
        self.getUser = self.cb.getUser
	self.port = None

    def startListening(self, port):
        if self.port:
            return
	self.factoryPreinit()
        self.factoryInit()
        self.factory.cb = self
	self.port = int(port)
        self.listener = self.factoryListen(self.port)
    
    def factoryListen(self, port):
        if self.personalRegistryValue('useSSL') and self.USESSL:
            return self.factoryListenSSL(port)
        else:
            return reactor.listenTCP(port, self.factory)

    def factoryListenSSL(self, port):
        ctx = gwssl.SBSSLContextFactory()
        ctx.cb = self
        return reactor.listenSSL(port, self.factory, ctx)
        
    def factoryPreinit(self):
        self.portalise()

    def portalise(self):
        if self.PORTALISE:
            self.cb.log.debug('using a twisted portal.')
            r = gwcred.SBRealm(self.USERCLASS)
            r.cb = self
            p = gwcred.SBPortal(r)
            c = gwcred.SBCredChecker()
            pkc = gwcred.SBPublicKeyChecker()
            c.cb = self
            pkc.cb = self
            p.cb = self
            p.registerChecker(c)
            p.registerChecker(pkc)
            self.portal = p
            self.FactoryClass.portal = p
        
    def authorised(self, user):
        self.cb.log.info('New gateway connection: %s', user.hostmask)
        self._connections.append(user)
	user.sendReply(self.mainRegistryValue('motd'), user.hostmask)
        
    
    def factoryInit(self, *args):
        self.factory = self.FactoryClass(*args)
        
    def stopListening(self):
        for c in self._connections:
            c.close()
        if self.listener:
            self.listener.stopListening()
            self.port = None

    class FactoryCLass:
        pass

class BaseUser(object):
    def close(self):
        self.user.clearAuth()
	self.cb._connections.remove(self)

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
