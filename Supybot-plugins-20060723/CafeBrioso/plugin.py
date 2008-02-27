###
# Copyright (c) 2004, Jeremiah Fincher
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

import re

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class CafeBrioso(callbacks.Privmsg):
    threaded=True
    _soupRe = re.compile(r'Soup</em></strong><br />(.*?)<br /><br />',re.M)
    _specialRe = re.compile(r'Special</span><br />(.*?)\n', re.M)
    def specials(self, irc, msg, args):
        """takes no arguments

        Gets the specials from Cafe Brioso's website.
        """
        try:
            html = utils.web.getUrl('http://www.cafebrioso.com/news.html')
        except utils.web.Error, e:
            irc.error(str(e), Raise=True)
        soupM = self._soupRe.search(html)
        if soupM is not None:
            soups = soupM.group(1)
            soups = soups.split('<br />')
        else:
            irc.error('Couldn\'t find today\'s soups.', Raise=True)
        specialM = self._specialRe.search(html)
        if specialM is not None:
            special = specialM.group(1)
            special = utils.web.htmlToText(special)
        else:
            irc.error('Couldn\'t find today\'s special.', Raise=True)
        irc.reply(format('Today\'s soups: %L; Today\'s special: %s.',
                         soups, special))
    specials = wrap(specials)


Class = CafeBrioso

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
