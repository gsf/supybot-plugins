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

# This plugin uses information from the website www.rhymezone.com. The
# information is freely available and fairly gathered in my opinion.
# I thank them deeply for providing this excellent service free, and extend
# the gratitude of any users of the plugin.

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re

BASEURL = ('http://www.rhymezone.com/r/rhyme.cgi'
        '?Word=%s&org1=syl&typeofrhyme=perfect&org2=sl')

WORDPATTERN = re.compile('HREF\="d\?.+?>(?P<foo>[a-zA-Z]+?)<')

class Rhyme(callbacks.Plugin):
    """The Rhyme plugin is a rhyming dictionary."""
    
    def rhymes(self, irc, msg, args, word):
        """<word>

        Displays a list of words rhyming with <word>"""
        
        html = utils.web.getUrl(BASEURL % word)
        L = WORDPATTERN.findall(html)
        resultCount = len(L)
        if resultCount:
            s = format('%n for %s: %L',
                (resultCount, 'rhyme'), word, self._sortResults(L))
            irc.reply(s)
        else:
            self._replyNoRhymes(irc)
    
    rhymes = wrap(rhymes, ['something'])

    def _replyNoRhymes(self, irc):
        if self.registryValue('replyIfNoRhymes'):
           irc.reply('No rhymes found.')
            
    def _sortResults(self, results):
        # I expect to add functionality here, like sort by letter/syllable
        # count
        L = results
        L.sort()
        return L
        
 


Class = Rhyme


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=78:
