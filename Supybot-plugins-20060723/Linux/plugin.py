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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Linux(callbacks.Plugin):
    """Add the help for "@plugin help Linux" here
    This should describe *how* to use this plugin."""
    threaded = True
    def callCommand(self, command, irc, msg, *args, **kwargs):
        try:
            super(Linux, self).callCommand(command,irc,msg,*args,**kwargs)
        except utils.web.Error, e:
            irc.error(str(e))

    def kernel(self, irc, msg, args):
        """takes no arguments

        Returns information about the current version of the Linux kernel.
        """
        fd = utils.web.getUrlFd('http://kernel.org/kdist/finger_banner')
        try:
            stable = 'unknown'
            snapshot = 'unknown'
            mm = 'unknown'
            for line in fd:
                (name, version) = line.split(':')
                if 'latest stable' in name:
                    stable = version.strip()
                elif 'snapshot for the stable' in name:
                    snapshot = version.strip()
                elif '-mm patch' in name:
                    mm = version.strip()
        finally:
            fd.close()
        irc.reply('The latest stable kernel is %s; '
                  'the latest snapshot of the stable kernel is %s; '
                  'the latest beta kernel is %s.' % (stable, snapshot, mm))
    kernel = wrap(kernel)


Class = Linux


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
