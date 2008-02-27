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
import email
import base64
from twisted.protocols import smtp
from twisted.internet import reactor, defer
from twisted.mail.protocols import ESMTPFactory
from twisted.protocols.imap4 import LOGINCredentials, PLAINCredentials

from gwbase import BasePlugin

RNL = '\n'

class MailUser(object):
    def __init__(self, user):
        self.user = user
        self.hostmask = user.gwhm
        self.rbuf = ''

    def sendReply(self, reply, inreply):
        self.rbuf = '%s\n[%s] %s' % (self.rbuf, inreply, reply)

    def getMessageDelivery(self):
        self.cb.authorised(self)
        md = ConsoleMessageDelivery()
        md.cb = self.cb
        md.smtpuser = self
        return md
        
    def reply(self):
        if len(self.rbuf):
            fad = 'supybot@supybot.supybot'
            msg = RNL.join(['From: %s' % fad,
                                'Reply-to: %s' % fad,
                                'Subject: %s' % 'Supybot Reply',
                                'To: %s' % self.address,
                                '',
                                self.rbuf])
            smtph = self.cb.personalRegistryValue('smtpHost')
            self.cb.cb.log.info('Replying to %s by email.', self.address)
            smtp.sendmail(smtph, fad, self.address , msg)
            self.rbuf = ''
            self.close

    def close(self):
        self.user.clearAuth()
        self.cb._connections.remove(self)

class SBESMTP(smtp.ESMTP):
    def authenticate(self, challenger):
        if self.portal:
            challenger.peer = self.peer
            challenge = challenger.getChallenge()
            coded = base64.encodestring(challenge)[:-1]
            self.sendCode(334, coded)
            self.mode = 'AUTH'
            self.challenger = challenger
        else:
            self.sendCode(454, 'Temporary authentication failure')

class MailGW(BasePlugin):
    PORTALISE = True
    USERCLASS = MailUser
    DEFAULT_PORT = 9025
    PROTOCOL = 'smtp'
    CONFIG_EXTRA = [('smtpHost', 'String', 'localhost',
                        """The address of the SMTP server used to send mail."""),
                    ('replyWait', 'Integer', 300,
                        """The number of seconds a session will last before 
                        completing and replying. Note that this is also the 
                        length of time smtp users will remain connected to 
                        receive walls.""")    ]
    def factoryInit(self, *args):
        self.factory = self.FactoryClass(self.portal)
        self.factory.portal = self.portal
        
    class FactoryClass(ESMTPFactory):
        protocol = SBESMTP
        def __init__(self, *a, **kw):
            ESMTPFactory.__init__(self, *a, **kw)
            self.delivery = ConsoleMessageDelivery()
            self.challengers = {
            'LOGIN': LOGINCredentials,
            'PLAIN': PLAINCredentials
            }

        def buildProtocol(self, addr):
            p = ESMTPFactory.buildProtocol(self, addr)
            #self.delivery.cb = self.cb
            #p.delivery = self.delivery
            p.peer = addr.host
            p.portal = self.portal
            return p

class ConsoleMessageDelivery:
    __implements__ = (smtp.IMessageDelivery,)
    
    def receivedHeader(self, helo, origin, recipients):
        return "Received: ConsoleMessageDelivery"
    
    def validateFrom(self, helo, origin):
        # All addresses are accepted
        return origin
    
    def validateTo(self, user):
        # Only messages directed to the "console" user are accepted.
        if user.dest.local == "supybot":
            return lambda: ConsoleMessage(self.smtpuser, self.cb)
        raise smtp.SMTPBadRcpt(user)

class ConsoleMessage:
    __implements__ = (smtp.IMessage,)
    
    def __init__(self, con, cb):
        self.lines = []
        self.cb = cb
        self.con = con
    def lineReceived(self, line):
        self.lines.append(line)
    
    def eomReceived(self):
        
        t = '\r\n'.join(self.lines)
        msg = email.message_from_string(t)
        if 'Reply-to' in msg:
            self.con.address = msg['Reply-to']
        elif 'From' in msg:
            self.con.address = msg['From']

                
        content = msg.get_payload().split('\r\n')
        for i, l in enumerate(content):
            reactor.callLater(2 * i,
                    self.cb.cb.receivedCommand, l, self.con)
        reactor.callLater(self.cb.personalRegistryValue('replyWait'),
            self.con.reply)

        self.lines = None
        return defer.succeed(None)
    
    def connectionLost(self):
        # There was an error, throw away the stored lines
        self.lines = None

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

