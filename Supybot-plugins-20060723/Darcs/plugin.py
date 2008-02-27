###
# Copyright (c) 2005, Jeremiah Fincher
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
import sys
import popen2

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

darcsCommandLine = utils.str.normalizeWhitespace("""
darcs pull
--repodir=%(REPODIR)s
--all
--verbose
--no-test
""".strip())

class Darcs(callbacks.Privmsg):
    def pull(self, irc, msg, args, repodirs):
        """[<repodir> [<repodir> [...]]]

        Does a darcs pull on <repodir>.  If <repodir> is not given, uses the
        default configured repodirs.
        """
        if not repodirs:
            repodirs = self.registryValue('repos')
        if not repodirs:
            irc.error('No repositories given.', Raise=True)
        for repodir in repodirs:
            inst = popen2.Popen4(darcsCommandLine % {'REPODIR': repodir})
            lines = [line.rstrip() for line in inst.fromchild]
            irc.replies(lines, prefixer='Darcs output: ', joiner='; ')
            ret = inst.wait()
            irc.reply(format('Darcs returned %i.', ret))
    pull = wrap(pull, ['owner', any('filename')])

    def install(self, irc, msg, args):
        """takes no arguments

        Does an install, executing the string supybot.plugins.Darcs.installCmd
        in an isolated process.
        """
        cmd = self.registryValue('installCmd')
        if not cmd:
            irc.error('No configured installCmd.', Raise=True)
        inst = popen2.Popen4(cmd)
        for line in inst.fromchild:
            self.log.info(line.rstrip())
        ret = inst.wait()
        irc.reply(format('%q returned %s.', cmd, ret))
    install = wrap(install, ['owner'])
            
    

Class = Darcs

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
