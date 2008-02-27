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

from gwssh import *

import code
import sys
import StringIO
from twisted.internet import defer

# generate a dictionary of what we need
def supylocaldict():
  from supybot import *
  #import supybot.conf as conf
  #import supybot.ircdb as ircdb
  #import supybot.utils as utils
  #import supybot.world as world
  #from supybot.commands import *
  #import supybot.plugins as plugins
  #import supybot.ircmsgs as ircmsgs
  #import supybot.ircutils as ircutils
  #import supybot.registry as registry
  #import supybot.callbacks as callbacks
  return locals()


class FileWrapper:
    softspace = 0
    state = 'normal'

    def __init__(self, o):
        self.o = o

    def flush(self):
        pass

    def write(self, data):
        self.o.sendReply(data.replace('\r\n', '\n'))

    def writelines(self, lines):
        self.write(''.join(lines))


class SBInterpreter(code.InteractiveInterpreter):
    def __init__(self, handler, _locals=None):
        print locals()
        code.InteractiveInterpreter.__init__(self, _locals)
        self.handler = handler
        self.resetBuffer()

    def push(self, cmd):
        print 'pushing'
        self.rbuf.append(cmd)
        c = '\n'.join(self.rbuf)
        o = sys.stdout
        sys.stdout = FileWrapper(self.handler)
        more = self.runsource(c, '<console>')
        sys.stdout = o
        if not more:
            self.resetBuffer()
        return more

    def write(self, msg):
        self.user.sendReply(msg)
   
    def resetBuffer(self):
        self.rbuf = []


class PyProtocol(SBProtocol):
    
    def connectionMade(self):
        self.more = False
        SBProtocol.connectionMade(self)
        self.interpreter = SBInterpreter(self.user, supylocaldict())
        self.interpreter.user = self.user

    def _linereceived(self, cmd):
        """ Received a line of data """
        self.more = self.interpreter.push(cmd)
        self.write_prompt()
    
    def write_prompt(self):
        p = (self.more and '... ') or '>>> '
        self.write(p)
        self.write(self.rbuf)

    def _receivedchr_4(self):
        """ Control-D handler """
        # We want to log out.
        self.user.close()

class PyTunnelSession(SshTunnelSession):
	WRAPPROTOCOL = PyProtocol

class PySession(ShellSession):
	ISESSION = PyTunnelSession

class PyUser(ShellUser):
    SESSIONCLASS = PySession
    def sendReply(self, reply, *a, **kw):
        self.con.write(reply.replace('\n', '\r\n'))
        if len(a):
            self.con.write(SNL)
            self.con.write(a[0])
            self.con.write(SNL)
            self.con.write_prompt()

class PyAuthServer(SBSSHUserAuthServer):
	USERCLASS = PyUser

class PyShellGW(ShellGW):
    PORTALISE = True
    USERCLASS = PyUser
    DEFAULT_PORT = 9024
    PROTOCOL = 'pyshell'
    USESSL = False
    CONFIG_EXTRA = []
    CAPABILITY = 'owner' 
    class FactoryClass(ShellGW.FactoryClass):
        services = {
            'ssh-userauth': PyAuthServer,
            'ssh-connection': connection.SSHConnection
        }
	
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

