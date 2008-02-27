###
# Copyright (c) 2004-2005, Kevin Murphy
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
import time

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Geekquote(callbacks.PluginRegexp):
    threaded = True
    callBefore = ['Web']
    regexps = ['geekSnarfer']

    def __init__(self, irc):
        self.__parent = super(Geekquote, self)
        self.__parent.__init__(irc)
        self.maxqdbPages = 403
        self.lastqdbRandomTime = 0
        self.randomData = {'qdb.us':[],
                            'bash.org':[]
                            }

    def callCommand(self, method, irc, msg, *L, **kwargs):
        try:
            self.__parent.callCommand(method, irc, msg, *L, **kwargs)
        except utils.web.Error, e:
            irc.error(str(e))

    _joiner = ' // '
    _qdbReString = r'<tr><td bgcolor="#(?:ffffff|e8e8e8)"><a href="/\d*?">'\
                    r'#\d*?</a>.*?<p>(?P<text>.*?)</p></td></tr>'
    _gkREDict = {'bash.org': re.compile(r'<p class="qt">(?P<text>.*?)</p>',
                    re.M | re.DOTALL),
                'qdb.us': re.compile(_qdbReString, re.M | re.DOTALL)}
    def _gkBackend(self, irc, msg, site, id):
        if not id:
            id = 'random'
        fetchData = True
        quote = ''
        if id == 'random':
            timeRemaining = int(time.time()) - self.lastqdbRandomTime
            if self.randomData[site]:
                quote = self.randomData[site].pop()
            else:
                if (site == 'qdb.us' and
                            int(time.time()) - self.lastqdbRandomTime <= 90):
                    id = 'browse=%s' % \
                         utils.iter.choice(xrange(self.maxqdbPages))
                quote = self._gkFetchData(site, id, random=True)
        else:
            quote = self._gkFetchData(site, id)
        irc.replies(quote.split(self._joiner), joiner=self._joiner)

    def _gkFetchData(self, site, id, random=False):
        html = ''
        try:
            html = utils.web.getUrl('http://%s/?%s' % (site, id))
        except utils.web.Error, e:
            self.log.info('%u server returned the error: %s',
                          site, utils.web.strError(e))
        s = None
        for item in self._gkREDict[site].finditer(html):
            s = item.groupdict()['text']
            s = self._joiner.join(s.splitlines())
            s = utils.web.htmlToText(s)
            if random and s:
                if s not in self.randomData[site]:
                    self.randomData[site].append(s)
            else:
                break
        if not s:
            return format('Could not find a quote for id %i.', id)
        else:
            if random:
                # To make sure and remove the first quote from the list so it
                self.randomData[site].pop()
            return s

    def geekSnarfer(self, irc, msg, match):
        r'http://(?:www\.)?(?P<site>bash\.org|qdb\.us)/\??(?P<id>\d+)'
        if not self.registryValue('geekSnarfer', msg.args[0]):
            return
        id = match.groupdict()['id']
        site = match.groupdict()['site']
        self.log.info('Snarfing geekquote %i from %s.', id, site)
        self._gkBackend(irc, msg, site, id)
    geekSnarfer = urlSnarfer(geekSnarfer)

    def geekquote(self, irc, msg, args, id):
        """[<id>]

        Returns a random geek quote from bash.org; the optional argument
        <id> specifies which quote to retrieve.
        """
        site = 'bash.org'
        self._gkBackend(irc, msg, site, id)
    geekquote = wrap(geekquote, [additional(('id', 'geekquote'))])

    def qdb(self, irc, msg, args, id):
        """[<id>]

        Returns a random geek quote from qdb.us; the optional argument
        <id> specifies which quote to retrieve.
        """
        site = 'qdb.us'
        self._gkBackend(irc, msg, site, id)
    qdb = wrap(qdb, [additional(('id', 'qdb'))])


Class = Geekquote


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
