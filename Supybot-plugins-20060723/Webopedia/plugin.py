###
# Copyright (c) 2004, Kevin Murphy
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

import supybot.utils as utils
from supybot.commands import *
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks


class Webopedia(callbacks.PluginRegexp):
    """Provides an interface to the webopedia.com technical term dictionary."""
    threaded = True
    callBefore = ['URL']
    regexps = ['termSnarfer']

    def __init__(self, irc):
        self.__parent = super(Webopedia, self)
        self.__parent.__init__(irc)

    def callCommand(self, method, irc, msg, *L, **kwargs):
        try:
            super(Webopedia, self).callCommand(method, irc, msg, *L, **kwargs)
        except utils.web.Error, e:
            irc.error(str(e))

    _joiner = ' // '
    _webopediaRe = re.compile(r'<!--content_start-->(?P<term>.*?)\<.*?<B>'\
                                r'(?P<definition>.*?)<!--content_stop-->',
                                re.M | re.DOTALL)
    _totdRe = re.compile(r'<!--content_start-->(?P<term>.*?)\<.*?</NOSCRIPT>'\
                            r'.*?</td>\s*</tr>(?P<definition>.*?)'\
                            r'<!--content_stop-->', re.M | re.DOTALL)
    def _wpBackend(self, irc, msg, term=None):
        site = 'www.webopedia.com'
        if not term:
            uri = 'totd.asp'
            regexp = self._totdRe
        else:
            webSafeTerm = '+'.join(term.split(' '))
            uri = 'SHARED/search_action.asp?term=%s' % webSafeTerm
            regexp = self._webopediaRe
        html = ''
        #print site
        #print uri
        try:
            html = utils.web.getUrl('http://%s/%s' % (site, uri))
        except utils.web.Error, e:
            self.log.info('%s server returned the error: %s' % \
                    (site, utils.web.strError(e)))
            irc.error('The server returned an unexpected error.  Contact the '\
                        'bot administrator for more information.')
        match = regexp.search(html)
        if match:
            s = match.groupdict()['definition']
            s = s.replace('<P>','\n')
            termResult = match.groupdict()['term'].strip().title()
            L = s.splitlines()
            cleanLines = [utils.web.htmlToText(line) for line in L]
            while '' in cleanLines:
                cleanLines.remove('')
            s = self._joiner.join(cleanLines)
            #s = utils.web.htmlToText(s)
            if not s:
                irc.error('Could not find a definition for the term "%s."' % term)
            else:
                if not term:
                    irc.reply('%s: %s' % (termResult, s))
                else:
                    irc.reply(s)
        else:
            irc.error('Could not find a definition for the term "%s."' % term)

    def termSnarfer(self, irc, msg, match):
        r'http://(?:www\.)webopedia.com/TERM/./(?P<term>.*?).html'
        if not self.registryValue('termSnarfer', msg.args[0]):
            return
        term = match.groupdict()['term']
        self.log.info('Snarfing webopedia term %s.' % term)
        self._wpBackend(irc, msg, term)
    termSnarfer = urlSnarfer(termSnarfer)

    def webopedia(self, irc, msg, args, term):
        """[<term>]

        Returns a definition from webopedia.com.  If <term> is not specified,
        the "Term of the Day" is returned.
        """
        self._wpBackend(irc, msg, term)
    webopedia = wrap(webopedia, [additional('text')])

Class = Webopedia

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
