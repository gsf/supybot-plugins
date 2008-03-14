###
# Copyright (c) 2008, Michael B. Klein
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

import kombat

class Kombat(callbacks.Plugin):

    def __init__(self,irc):
        reload(kombat)
        super(callbacks.Plugin,self).__init__(irc)

    def build_response(self,result):
        if isinstance(result['data'],str):
            return "%s's %s: %s" % (result['used'][1], result['used'][-1], result['data'])
        else:
            keys = result['data'].keys()
            keys.sort()
            return "kombat " + " ".join(result['used']) + " <" + " | ".join(keys) + ">"
        
    def kombat(self, irc, msg, args):
        """<version (I,II)> [<fighter>] [<move>...]
        """
        result = { 'data' : utils.gen.InsensitivePreservingDict(kombat.moves_data), 'remaining' : args, 'used' : [] }
        while len(result['remaining']) > 0:
            if isinstance(result['data'],dict) or isinstance(result['data'],utils.gen.InsensitivePreservingDict):
                key = result['remaining'][0]
                result['remaining'] = result['remaining'][1:]
                if key in result['data']:
                    result['data'] = result['data'][key]
                    if isinstance(result['data'],dict):
                        result['data'] = utils.gen.InsensitivePreservingDict(result['data'])
                    result['used'].append(key)
                else:
                    break
            else:
                break
        irc.reply(self.build_response(result),prefixNick=True)

Class = Kombat

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
