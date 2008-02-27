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

import os
import md5
from twisted.conch import avatar, credentials
from Crypto.PublicKey import RSA
from twisted.python import components
from twisted.internet import reactor, protocol
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.ssh import factory, userauth, connection, keys, session
from twisted.conch.ssh import common, channel

from gwbase import BasePlugin

RNL = '\r'
SNL = '\r\n'

# Escape sequence:
ESC = ''.join(map(chr, [27, 91]))

# Backspace sequence:
# . Backspace-Space-Backspace.
BS = ''.join(map(chr, [8, 32, 8]))

class SBProtocol(protocol.Protocol):
    """ the protocol that gets wrapped in SSH """
    def connectionMade(self):
        """ called on connection """
        self.rbuf = ''
        self.cb.authorised(self.user)
    
    def connectionLost(self, reason):
        """ Called on loss of connection. """
        self.cb._connections.remove(self.user)
        #self.user.user.clearAuth()

    def loseConnection(self):
        self.transport.loseConnection()
        
    def dataReceived(self, data):
        """ called on receipt of data """
        self._processdata(data)
        rl = len(self.rbuf)
        if rl:
            if rl > 512:
                # Close the connecion if the read buffer is getting too large.
                self.loseConnection()
            else:
                # Otherwise process it.
                self._processreadbuf()

    def _processdata(self, data):
        """ Process individual characters in the stream """
        for c in data:
            cc = ord(c)
            doname = '_receivedchr_%s' % cc
            
            if hasattr(self, doname):
                # we have a special handler for this character
                getattr(self, doname)()
            else:
                # this this a general character
                self._receivedchr_general(c)

    def _processreadbuf(self):
        
        lines = self.rbuf.split(RNL)
        if len(lines) > 1:
        # we have a return
            # remove the last element, will be empty
            self.rbuf = ''
            lines.pop()
            for l in lines:
                self._linereceived(l)

    def _linereceived(self, cmd):
        """ Received a line of data """
        if len(cmd):
            self.cb.cb.receivedCommand(cmd, self.user)
            self.write_prompt()

    # The general character handler
    def _receivedchr_general(self, c):
        """ Handle all other keys """
        self.rbuf = '%s%s' % (self.rbuf, c)
        self.write(c)
       
    # The special character handlers
    def _receivedchr_3(self):
        """ Control-C handler """
        # We want to escape the line and clear the buffer.
        self.transport.write(SNL)
        self.rbuf = ''
        self.write_prompt()

    def _receivedchr_4(self):
        """ Control-D handler """
        # We want to log out.
        self._linereceived('logout')

    def _receivedchr_13(self):
        """ Return key handler """
        # We want to add the 13 to the buffer, but echo back a full newline.
        #if len(self.rbuf):
        self.write(SNL)
        self.rbuf = '%s%s' % (self.rbuf, RNL)
    
    def _receivedchr_27(self):
        self.rbuf = '%s%s' % (self.rbuf, chr(27))
        
    def _receivedchr_91(self):
        if self.rbuf.endswith(chr(27)):
            self.rbuf = '%s%s' % (self.rbuf, chr(91))
        else:
            self._receivedchr_general(chr(91))
        
    def _receivedchr_65(self):
        """ Up key handler """
        if self.rbuf.endswith(ESC):
            self.rbuf = self.rbuf[:-2]
        else:
            self._receivedchr_general(chr(65))
    
    def _receivedchr_66(self):
        """ Down key handler """
        if self.rbuf.endswith(ESC):
            self.rbuf = self.rbuf[:-2]
        else:
            self._receivedchr_general(chr(66))
                    
    def _receivedchr_67(self):
        """ Left key handler """
        if self.rbuf.endswith(ESC):
            self.rbuf = self.rbuf[:-2]
        else:
            self._receivedchr_general(chr(67))
                    
    def _receivedchr_68(self):
        """ Left key handler """
        if self.rbuf.endswith(ESC):
            self.rbuf = self.rbuf[:-2]
        else:
            self._receivedchr_general(chr(68))
       
    def _receivedchr_127(self):
        """ backspace handler """
        if len(self.rbuf) > 0:
            self.write(BS)
            self.rbuf = self.rbuf[:-1]
    
    def write(self, msg):
        reactor.callLater(0, self.transport.write, msg)
    
    def write_reply(self, msg=''):
        self.write('%s\r\n' % msg)
        self.write_prompt()
        
    def write_prompt(self):
        self.write('%s@%s: $ %s' % \
        (self.user.user.name, self.cb.cb.getNick(), self.rbuf))

class SshTunnelSession(object):
    WRAPPROTOCOL = SBProtocol
    """ class representing each connected SSH client """
    def __init__(self, avatar):
        self.cb = avatar.cb
        self.avatar = avatar
        self.cb.cb.log.critical('%s' % avatar.__class__)

    def getPty(self, term, windowSize, attrs):
        pass

    def closed(self):
        self.ep.loseConnection()
        
    def execCommand(self, proto, cmd):
        pass
        
    def openShell(self, trans):
        """ called back on a successful connection """
        
        # Instantiate the protocol.
        self.ep = self.WRAPPROTOCOL()
        self.avatar.con = self.ep
        self.ep.user = self.avatar
        self.ep.cb = self.cb

        # the peer information
        self.ep.peer = self.avatar.conn.transport.transport.getPeer()
        # . method from the actual transport.
        #self.ep.loseRealConnection = self.avatar.conn.transport.transport.loseConnection
        # Twisted black magic
        self.ep.makeConnection(trans)
        trans.makeConnection(session.wrapProtocol(self.ep))

class ShellSession(session.SSHSession):
    ISESSION = SshTunnelSession
    name = 'session'
    def __init__(self, *args, **kw):
        channel.SSHChannel.__init__(self, *args, **kw)
        self.buf = ''
        self.session = self.ISESSION(self.avatar)

class ShellUser(avatar.ConchUser):
    SESSIONCLASS=ShellSession
    def __init__(self, user):
        avatar.ConchUser.__init__(self)
        self.user = user
        self.hostmask = user.gwhm
        #self.channelLookup.update({'session':session.SSHSession})
    
    def lookupChannel(self, channelType, windowSize, maxPacket, data):
        return self.SESSIONCLASS(remoteWindow = windowSize,
                                remoteMaxPacket = maxPacket,
                                data=data, avatar=self)
    
    def sendReply(self, reply, inreply, **kw):
        self.con.write_reply('\r\n[%s] %s' % (inreply, reply))

    def close(self):
        self.user.clearAuth()
        self.con.loseConnection()

class SBSSHUserAuthServer(userauth.SSHUserAuthServer):
        USERCLASS = ShellUser
        def auth_password(self, packet):
            password = userauth.getNS(packet[1:])[0]
            c = userauth.credentials.UsernamePassword(self.user, password)
            c.peer = self.transport.transport.getPeer().host
            return self.portal.login(c, None, self.USERCLASS).addErrback(
                                                        self._ebPassword)
        def auth_publickey(self, packet):
            NS = userauth.NS
            hasSig = ord(packet[0])
            algName, blob, rest = userauth.getNS(packet[1:], 2)
            pubKey = userauth.keys.getPublicKeyObject(data = blob)
            b = NS(self.transport.sessionID) + chr(userauth.MSG_USERAUTH_REQUEST) + \
                NS(self.user) + NS(self.nextService) + NS('publickey') + \
                chr(hasSig) +  NS(keys.objectType(pubKey)) + NS(blob)
            signature = hasSig and userauth.getNS(rest)[0] or None
            c = credentials.SSHPrivateKey(self.user, blob, b, signature)
            c.peer = self.transport.transport.getPeer().host
            return self.portal.login(c, None, self.USERCLASS).addErrback(
                                                        self._ebCheckKey,
                                                        packet[1:])

class ShellGW(BasePlugin):
    PORTALISE = True
    USERCLASS = ShellUser
    DEFAULT_PORT = 9022
    PROTOCOL = 'ssh'
    USESSL = False
    CONFIG_EXTRA = []
    def factoryPreinit(self):
        BasePlugin.factoryPreinit(self)
        sshdir = self.cb.datapaths['keys.ssh']
        keypath = '%s%s%s' % (sshdir, os.sep,
            self.mainRegistryValue('keys.rsaKeyFile'))

        if not os.path.exists(keypath):
            raise Exception, 'The SSH private key is missing'
        pubpath = '%s.pub' % keypath
        if not os.path.exists(pubpath):
            raise Exception, 'The SSH public key is missing'
        
        self.FactoryClass.publicKeys = {'ssh-rsa':keys.getPublicKeyString(filename=pubpath)}
        self.FactoryClass.privateKeys = {'ssh-rsa':keys.getPrivateKeyObject(filename=keypath)}
        
         
    class FactoryClass(factory.SSHFactory):
        services = {
            'ssh-userauth': SBSSHUserAuthServer,
            'ssh-connection': connection.SSHConnection
        }

        def startFactory(self):
            # disable coredumps
            if factory.resource:
                factory.resource.setrlimit(factory.resource.RLIMIT_CORE, (0,0))
            else:
                self.cb.log.debug('SSH: INSECURE: unable to disable core dumps.')
            if not hasattr(self,'publicKeys'):
                self.publicKeys = self.getPublicKeys()
            if not hasattr(self,'privateKeys'):
                self.privateKeys = self.getPrivateKeys()
            if not self.publicKeys or not self.privateKeys:
                raise error.ConchError('no host keys, failing')
            if not hasattr(self,'primes'):
                self.primes = self.getPrimes()
                #if not self.primes:
                #    log.msg('disabling diffie-hellman-group-exchange because we cannot find moduli file')
                #    transport.SSHServerTransport.supportedKeyExchanges.remove('diffie-hellman-group-exchange-sha1')
                if self.primes:
                    self.primesKeys = self.primes.keys()

        def getDHPrime(self, bits):
            """
            Return a tuple of (g, p) for a Diffe-Hellman process, with p being as
            close to bits bits as possible.
 
            @type bits: C{int}
            @rtype:     C{tuple}
            """
            self.primesKeys.sort(lambda x,y,b=bits:cmp(abs(x-b), abs(x-b)))
            realBits = self.primesKeys[0]
            return random.choice(self.primes[realBits])
       
        def buildProtocol(self, addr):
            t = factory.transport.SSHServerTransport()
            t.supportedPublicKeys = self.privateKeys.keys()
            if not self.primes:
                ske = t.supportedKeyExchanges[:]
                ske.remove('diffie-hellman-group-exchange-sha1')
                t.supportedKeyExchanges = ske
            t.factory = self
            return t

def keygen(filepath):
        key = RSA.generate(1024, common.entropy.get_bytes)
        
        # Create and write the private key file.
        # . Generate the string.
        privk = keys.makePrivateKeyString(key)
        # . Write the file
        privf = open(filepath, 'w')
        privf.write(privk)
        privf.close()
        # . Fix the permissions
        os.chmod(filepath, 33152)
        
        # Create and write the public key file.
        # . Generate the string.
        pubk = keys.makePublicKeyString(key)
        # . Write the file.
        pubf = open('%s.pub' % filepath, 'w')
        pubf.write(pubk)
        pubf.close()


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
