###
# Copyright (c) 2011, Michael B. Klein
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
import re

class PDPC(callbacks.Plugin):
    
    def pdpc(self, irc, msg, args, channel):
      """
      Display in-channel supporters of the Peer-Directed Projects Center 
      <http://freenode.net/pdpc.shtml> based on cloaked nicks."""
      tag = re.compile('@pdpc$')
      contributors = []
      for u in irc.state.channels[channel].users:
        parts = irc.state.nickToHostmask(u).split('/')
        if tag.search(parts[0]):
          level = parts[2]
          contributors.append('%s (%s)' % (parts[3], parts[2]))
      irc.reply('PDPC supporters in %s: %s' % (channel, ', '.join(contributors)), prefixNick=False)
      
    pdpc = wrap(pdpc, ['inChannel'])
    
    def conf(self, irc, msg, args, channel):
      """
      Display users with a conference-cloaked nick."""
      tag = re.compile('@conference/code4lib')
      contributors = []
      for u in irc.state.channels[channel].users:
        if tag.search(irc.state.nickToHostmask(u)):
          contributors.append(u)
      irc.reply('Conference attendees in %s: %s' % (channel, ', '.join(contributors)), prefixNick=False)

    conf = wrap(conf, ['inChannel'])
      
Class = PDPC


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
