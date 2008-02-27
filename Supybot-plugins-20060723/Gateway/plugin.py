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
import supybot.ircdb as ircdb
import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks
import base64, binascii
import os
import inspect

from twisted.python import log as tlog
tlog.startLogging(file('/home/ali/stlog', 'w'))
print dir(tlog)
from gwplugins import plugins as PLUGINLIST

# Converter to check capability.
def gatewayCapable(irc, msg, args, state):
    capability = state.cb.registryValue('capability')
    if not ircdb.checkCapability(msg.prefix, capability):
        irc.errorNoCapability(capability, Raise=True)

# Converter to check source.
def gatewaySource(irc, msg, args, state):
    con = msg.fromGateway
    if con:
        state.args.append(con)
    else:
        irc.error('This command may only be called from Gateway connections',
                    Raise = True)

# Add the converters.
addConverter('gatewaySource', gatewaySource)
addConverter('gatewayCapable', gatewayCapable)

# The plugin class.
class Gateway(callbacks.Privmsg):
    """Gateway allows users to connect to the bot via various network
    protocols. Please read the README.txt file if you are the bot owner."""

    def __init__(self, irc):
        callbacks.Privmsg.__init__(self, irc)
        self._available = {}
        self.datapaths = {}
        self.irc = world.ircs[0]
        self.createDirectories()
        self.importProtocols()
        self.autoStart()

    def outFilter(self, irc, msg):
        if msg.inReplyTo:
            if msg.inReplyTo.fromGateway:
                con = msg.inReplyTo.fromGateway
                con.sendReply(msg.args[1], msg.inReplyTo.args[1],
                    msg=msg)
                return None
            else:
                return msg
        else:
            return msg
    
    def die(self):
        for p in self._available:
            self._available[p].stopListening()
       
    def logout(self, irc, msg, args, con):
        """takes no arguments

        Log out of a gateway session. This may only be called from a gateway
        session."""
        # sending a reply is usually too slow so we don't bother
        #con.sendReply('logging out', 'logout')
        con.user.clearAuth()
        con.close()
       
    logout = wrap(logout, ['gatewaySource'])
    
    def say(self, irc, msg, args, user, text):
        """<user> <text>

        Say <text> to <user>, where <user> is the username of a user connected
        to the gateway."""
        found = False
        nick = self.getMsgNick(msg)
        for p in self._available:
            pr = self._available[p]
            if pr.port:
                for c in pr._connections:
                    if c.user.name == user:
                        c.sendReply('from %s: %s' % (nick, text), 'say')
                        found = True

        if found:
            irc.replySuccess()
        else:
            irc.replyError('User is not connected to the gateway')
    say = wrap(say, ['gatewayCapable', 'something', 'text'])

    def wall(self, irc, msg, args, text):
        """<text>

        Say <text> to all users connected to the Gateway."""
        nick = self.getMsgNick(msg)
        found = False
        for p in self._available:
            pr = self._available[p]
            if pr.port:
                for c in pr._connections:
                    c.sendReply('from %s: %s' % (nick, text), 'wall')
                    found = True
        if found:
            irc.replySuccess()
        else:
            irc.replyError('There are no users connected to the Gateway.')
    
    wall = wrap(wall, ['gatewayCapable', 'text'])
    
    def available(self, irc, msg, args):
        """takes no arguments

        Returns a list of supported network protocols."""
        L = [s.PROTOCOL for s in self._available.values()]
        irc.reply(format('%L', L))

    available = wrap(available, ['gatewayCapable'])

    def running(self, irc, msg, args):
        """takes no arguments

        Returns a list of running network daemons, and their ports."""
        L = ['%s on %s' % (s.PROTOCOL,
                    s.port) for s in self._available.values() if s.port]
        if len(L):
            irc.reply(format('%L', L))
        else:
            irc.reply(format('%s', 'There are no running gateways.'))
        
    running = wrap(running, ['gatewayCapable'])
        
    def start(self, irc, msg, args, protocol, port):
        """<protocol> <port>

        Start the server named by <protocol>."""
        # needs changing
        p = protocol
        if p in self._available:
            if not self._available[p].port:
                if not port:
                    port = \
                    self._available[p].personalRegistryValue('defaultPort')
                self._available[p].startListening(port)
                irc.replySuccess()
            else:
                irc.reply('Error: Already running')

    start = wrap(start, ['owner', 'something', optional('int')])

    def stop(self, irc, msg, args, protocol):
        """<protocol>

        Stop the server named by <protocol>."""

        for p in self._available:
            if p == protocol:
                self._available[p].stopListening()
                irc.replySuccess()

    stop = wrap(stop, ['owner', 'something'])

    def users(self, irc, msg, args):
        """takes no arguments

        Returns a list of users connected to the gateway."""
        rl = []
        for p in self._available:
            pr = self._available[p]
            if pr.port:
                nc = len(pr._connections)
                hml = []
                for i in pr._connections:
                    hml.append(i.user.name)
                if nc:
                    rl.append('%s %s (%s)' % (p, nc, format('%L', hml)))
        if len(rl):
            irc.reply(format('Users connected to the gateway: %L.', rl))
        else:
            irc.reply('There are no users connected to the gateway.')
    
    def receivedCommand(self, cmd, con):
        """ handle a single command """
        cmd = cmd.strip()
        self.log.debug('Received command %s from %s.',
                        cmd,
                        con.hostmask)
        to = self.getNick()
        m =  ircmsgs.privmsg(self.getNick(), cmd, con.hostmask)
        # tag it with the connection so we can pick up the reply
        m.tag('fromGateway', con)
        # feed the message
        world.ircs[0].feedMsg(m)

    def getUser(self, **kw):
        """ will return a user object tagged with a hostmask for use or None
        """
        if 'protocol' not in kw:
            raise KeyError, 'Need a protocol name'
        else:
            user = None
            if 'username' not in kw:
                raise KeyError, 'Need a username'
            try:
                user = ircdb.users.getUser(kw['username'])
            except KeyError:
                return False
            cap = self.registryValue('capability')
            pcap = self.registryValue('%s.capability' % kw['protocol'])
            if cap:
                if not ircdb.checkCapability(kw['username'], cap):
                    return False
            if pcap:
                if not ircdb.checkCapability(kw['username'], pcap):
                    return False
            if 'password' in kw:
                if not user.checkPassword(kw['password']):
                    return False
            elif 'blob' in kw:
                if not self.checkKey(kw['username'], kw['blob']):
                    return False
            else:
                return False
            user.gwhm = self.buildHostmask(kw['username'], kw['protocol'],
                    kw['peer'])
            user.addAuth(user.gwhm)
            return user
           
    def checkKey(self, un, blob):
        keypath = '%s%s%s' % \
            (self.datapaths['keys.ssh.authorized'],
                os.sep, un)
        if not os.access(keypath, os.F_OK):
            self.log.debug('No key file for user')
            return False
        else:
            f = open(keypath)
            for line in f:
                self.log.critical('doing a line')
                l = line.split()
                if len(l) > 2:
                    try:
                        if base64.decodestring(l[1]) == blob:
                            self.log.critical('Yes!')
                            return 1
                    except binascii.Error:
                        pass
            return 0

           
    def buildHostmask(self, un, protocol, peer):
        """ build a new partly random hostmask and return it """
        return '%s%s!%s@%s' % (protocol, utils.mktemp()[:9], un, peer)
      
    def buildAnonymousHostmask(self, protocol, peer):
        return self.buildHostmask('Anonymous', protocol, peer)
    
    def getNick(self):
        return world.ircs[0].nick
        
    def createDirectories(self):
        self.datapaths['root'] = conf.supybot.directories.data.dirize('Gateway')
        self.createIfNotExistingDir(self.datapaths['root'])
        self.datapaths['keys'] = '%s%s%s' % (self.datapaths['root'], os.sep, 'keys')
        self.createIfNotExistingDir(self.datapaths['keys'])
        self.datapaths['keys.ssl'] = '%s%sssl' % (self.datapaths['keys'], os.sep)
        self.createIfNotExistingDir(self.datapaths['keys.ssl'])
        self.datapaths['keys.ssh'] = '%s%sssh' % (self.datapaths['keys'], os.sep)
        self.createIfNotExistingDir(self.datapaths['keys.ssh'])
        self.datapaths['keys.ssh.authorized'] = '%s%sauthorized' % \
            (self.datapaths['keys.ssh'], os.sep)
        self.createIfNotExistingDir(self.datapaths['keys.ssh.authorized'])
        self.datapaths['protocols'] = '%s%s%s' % (self.datapaths['root'], os.sep, 'protocols')
        self.createIfNotExistingDir(self.datapaths['protocols'])

    def createIfNotExistingDir(self, path):
        if not os.access(path, os.F_OK):
            os.mkdir(path)
    
    def getMsgNick(self, msg):
        con = msg.fromGateway
        nick = ''
        if con:
            nick = con.user.name
        else:
            nick = msg.nick
        return nick

    def importProtocols(self):
        for c in PLUGINLIST:
            s = c.PROTOCOL
            self._available[s] = c(self)
            self.datapaths['protocols.%s' % s] = '%s%s%s' % \
                (self.datapaths['protocols'], os.sep, s)
            self.createIfNotExistingDir(self.datapaths['protocols.%s' % s])
    
    def autoStart(self):
        for p in self._available:
            if self.registryValue('%s.autoStart' % p):
                port = self.registryValue('%s.defaultPort' % p)
                self._available[p].startListening(port)

    #def isCommand(self, name):
    #    self.log.critical('%s %s', name, name in self._commands)
    #    return (name in self._commands) or callbacks.Privmsg.isCommand(self, name)

    #def getCommand(self, name):
    #    """Gets the given command from this plugin."""
    #    name = callbacks.canonicalName(name)
    #    assert self.isCommand(name), '%s is not a command.' % \
    #                                 utils.quoted(name)
    #    if name in self._commands:
    #        return self._commands[name]
    #    else:
    #        return getattr(self, name)
         
    
    dirize = conf.supybot.directories.data.dirize

Class = Gateway

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
