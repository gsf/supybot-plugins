#!/usr/bin/python

###
# Copyright (c) 2004-2005, Jeremiah Fincher
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

import supybot

import supybot.plugins as plugins

import gc
import sys
import heapq
import socket
import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Supybot(callbacks.Privmsg):
    def __init__(self, irc):
        self.__parent = super(Supybot, self)
        self.__parent.__init__(irc)
        self.whos = {}

    def maxrefs(self, irc, msg, args, max):
        """[<max>]

        Returns the <max> objects with the largest refcounts.  <max> defaults
        to 10.
        """
        q = [None]*max
        for o in gc.get_objects():
            t = (sys.getrefcount(o), o)
            if t > q[0]:
                heapq.heapreplace(q, t)
        L = []
        while q:
            L.append(heapq.heappop(q))
        L.reverse()
        utils.mapinto('%s: %r'.__mod__, L)
        irc.reply(format('%L', L))
    maxrefs = wrap(maxrefs, [additional('int', 10)])
        
    def botsnack(self, irc, msg, args):
        """takes no arguments

        Acts as if the bot was given a snack.
        """
        irc.reply('Botsnacks are stupid, donate to my SF.net project instead.')
    botsnack = wrap(botsnack)
        
    def fincher(self, irc, msg, args, filename):
        """<filename>

        Returns a link to <filename> on jemfinch's website.
        """
        filename = utils.web.urlquote(filename)
        irc.reply('http://www.cse.ohio-state.edu/~fincher/' + filename)
    fincher = wrap(fincher, [rest('filename')])

    def servtest(self, irc, msg, args, host, port):
        """<host> <port>

        Returns whether the <host> is accepting connections on <port>.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            irc.reply('Server at %s:%s is up.' % (host, port))
        except socket.error, e:
            irc.reply('Server at %s:%s is not up (%s)' % (host, port, e))
    servtest = wrap(servtest, ['something', 'int'])
            
    def who(self, irc, msg, args, mask):
        """[<mask>]

        Returns the nicks of all users matching <mask> on this network.  If
        <mask> is not given, '*supybot*' will be used.
        """
        self.whos[mask] = (irc, [])
        irc.queueMsg(ircmsgs.who(mask))
    who = wrap(who, [additional('something', '*supybot*')])

    def do352(self, irc, msg):
        for mask in self.whos:
            if ircutils.hostmaskPatternEqual(mask, str(msg)):
                self.whos[mask][1].append(msg)

    def do315(self, irc, msg):
        mask = msg.args[1]
        if mask in self.whos:
            (replyIrc, msgs) = self.whos.pop(mask)
            nicks = []
            for msg in msgs:
                nicks.append(msg.args[5])
            utils.sortBy(ircutils.toLower, nicks)
            if nicks:
                replyIrc.reply(format('%s matched: %L.', len(nicks), nicks))
            else:
                replyIrc.reply('No users matched %s.' % mask)


Class = Supybot

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
