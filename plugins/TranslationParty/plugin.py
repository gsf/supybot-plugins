###
# Copyright (c) 2010, Michael B. Klein
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
import sys
from random import randrange
import simplejson
from urllib import quote, urlencode
from urllib2 import urlopen, urlparse, Request, build_opener, HTTPError
from BeautifulSoup import BeautifulStoneSoup

class TranslationParty(callbacks.Plugin):
    """Add the help for "@plugin help TranslationParty" here
    This should describe *how* to use this plugin."""
    
    def _translate(self, from_lang, to_lang, text):
        params = { 'langpair' : '|'.join((from_lang,to_lang)), 'q' : text.encode('utf8'), 
            'key' : 'notsupplied', 'v' : '1.0', 'nocache' : randrange(0,sys.maxint) }
        url = 'http://www.google.com/uds/Gtranslate?' + urlencode(params)
        response = simplejson.loads(urlopen(url).read())
        translation = unicode(BeautifulStoneSoup(response['responseData']['translatedText'],convertEntities=BeautifulStoneSoup.HTML_ENTITIES))
        return translation
    
    def _party(self, from_lang, to_lang, text):
        stack = [text]
        stack.append(self._translate(from_lang, to_lang, stack[-1]))
        stack.append(self._translate(to_lang, from_lang, stack[-1]))
        stack.append(self._translate(from_lang, to_lang, stack[-1]))
        stack.append(self._translate(to_lang, from_lang, stack[-1]))
        while (len(stack) < 50) and ((stack[-2] != stack[-4]) and (stack[-1] != stack[-3])):
            stack.append(self._translate(from_lang, to_lang, stack[-1]))
            stack.append(self._translate(to_lang, from_lang, stack[-1]))
        return(stack)
        
    def translationparty(self, irc, msg, args, opts, text):
        """[--lang <iso-code>] [--all] <text>
        Try to find equilibrium in back-and-forth translations of <text>. Language defaults to 'ja' (Japanese)."""
        lang = 'ja'
        show_all = False
        
        for (opt,arg) in opts:
            if opt == 'lang':
                lang = arg
            if opt == 'all':
                show_all = True
        
        result = self._party('en', lang, text)
        if len(result) < 50:
            irc.reply("Equilibrium found!")
        else:
            irc.reply("It is doubtful that this phrase will ever reach equilibrium.")

        if show_all:
            irc.reply(" -> ".join(result).encode('utf8'))
        else:
            irc.reply(" -> ".join((result[0],result[-1])).encode('utf8'))
        
    translationparty = wrap(translationparty, [getopts({'lang':'something','all':''}), 'text'])
        
Class = TranslationParty


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
