
from gwssh import *
from twisted.python import components
import cPickle as Pickle
from twisted.conch.ssh import session

class PickleProtocol(SBProtocol):
    def write_prompt(self):
        pass

class PickleTunnelSession(SshTunnelSession):
	WRAPPROTOCOL = PickleProtocol

class PickleSession(ShellSession):
	ISESSION = PickleTunnelSession

class PickleUser(ShellUser):
    SESSIONCLASS = PickleSession
    def sendReply(self, reply, inreply, **kw):
        if 'msg' in kw:
            s = Pickle.dumps(kw['msg'])
            self.con.write(s)

class PickleAuthServer(SBSSHUserAuthServer):
	USERCLASS = PickleUser

class PickleGW(ShellGW):
    PORTALISE = True
    USERCLASS = PickleUser
    DEFAULT_PORT = 9023
    PROTOCOL = 'pickle'
    USESSL = False
    CONFIG_EXTRA = []
    
    class FactoryClass(ShellGW.FactoryClass):
        services = {
            'ssh-userauth': PickleAuthServer,
            'ssh-connection': connection.SSHConnection
        }
	
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

