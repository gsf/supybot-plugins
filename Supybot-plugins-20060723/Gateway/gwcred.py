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
from twisted.cred import portal, checkers, credentials, error
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.conch.credentials import ISSHPrivateKey
from twisted.python import failure
from twisted.internet import defer
from twisted.conch.ssh import keys

class SBCredChecker(object):
    """ SSH Username and Password Credential checker """
    # this implements line tells the portal that we can handle un/pw
    __implements__ = (checkers.ICredentialsChecker,)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def requestAvatarId(self, credentials):
        self.cb.log.debug('twisted checker checking %s',
		credentials.username)
        """ Return an avatar id or return an error """
        a = self.cb.getUser(protocol=self.cb.PROTOCOL,
            username=credentials.username,
            password=credentials.password,
            peer=credentials.peer)
        if a:
            return a
        else:
            return failure.Failure(error.UnauthorizedLogin())

class SBPublicKeyChecker(object):
    """ Public key checker """
    __implements__ = (checkers.ICredentialsChecker,)
    credentialInterfaces = (ISSHPrivateKey,)

    def requestAvatarId(self, credentials):
        a = self.cb.getUser(protocol=self.cb.PROTOCOL,
                        username=credentials.username,
                        blob=credentials.blob,
                        peer=credentials.peer)
            #except:
            #    pass
        if a:
            return a
        else:
            return failure.Failure(error.UnauthorizedLogin())

#class SBPublicKeyChecker(SSHPublicKeyDatabase):
#    credentialInterfaces = ISSHPrivateKey,
#    __implements__ = ICredentialsChecker
#
#    def requestAvatarId(self, credentials):
#        if not self.checkKey(credentials):
#            return defer.fail(UnauthorizedLogin())
#        if not credentials.signature:
#            return defer.fail(error.ValidPublicKey())
#        else:
#            try:
#                pubKey = keys.getPublicKeyObject(data = credentials.blob)
#                if keys.verifySignature(pubKey, credentials.signature,
#                                        credentials.sigData):
#                    return defer.succeed(credentials.username)
#            except:
#                pass
#        return defer.fail(UnauthorizedLogin())
#
#    def checkKey(self, credentials):
#        sshDir = os.path.expanduser('~%s/.ssh/' % credentials.username)
#        if sshDir.startswith('~'): # didn't expand
#            return 0
#        uid, gid = os.geteuid(), os.getegid()
#        ouid, ogid = pwd.getpwnam(credentials.username)[2:4]
#        os.setegid(0)
#        os.seteuid(0)
#        os.setegid(ogid)
#        os.seteuid(ouid)
#        for name in ['authorized_keys2', 'authorized_keys']:
#            if not os.path.exists(sshDir+name):
#                continue
#            lines = open(sshDir+name).xreadlines()
#            os.setegid(0)
#            os.seteuid(0)
#            os.setegid(gid)
#            os.seteuid(uid)
#            for l in lines:
#                l2 = l.split()
#                if len(l2) < 2:
#                    continue
#                try:
#                    if base64.decodestring(l2[1]) == credentials.blob:
#                        return 1
#                except binascii.Error:
#                    continue
#        return 0




class SBPortal(portal.Portal):
    pass

class SBRealm:
    __implements__ = portal.IRealm

    def __init__(self, userclass):
        self.userclass = userclass
    
    def requestAvatar(self, avatarId, mind, *interfaces):
        self.cb.cb.log.critical('%s', interfaces)
        av = self.userclass(avatarId)
        av.cb = self.cb
        return interfaces[0], av, lambda: None

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:



