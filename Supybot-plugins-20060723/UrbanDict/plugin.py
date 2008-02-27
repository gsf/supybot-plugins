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

import SOAP

import supybot.utils as utils
from supybot.commands import *
import supybot.callbacks as callbacks


class UrbanDict(callbacks.Plugin):
    threaded = True
    server = SOAP.SOAPProxy('http://api.urbandictionary.com/soap')

    def _licenseCheck(self, irc):
        license = self.registryValue('licenseKey')
        if not license:
            irc.error('You must have a free UrbanDictionary API license key '
                      'in order to use this command.  You can get one at '
                      '<http://www.urbandictionary.com/api.php>.  Once you '
                      'have one, you can set it with the command '
                      '"config supybot.plugins.UrbanDict.licenseKey <key>".',
                      Raise=True)
        return license

    def urbandict(self, irc, msg, args, words):
        """<phrase>

        Returns the definition and usage of <phrase> from UrbanDictionary.com.
        """
        license = self._licenseCheck(irc)
        definitions = self.server.lookup(license, ' '.join(words))
        if not len(definitions):
            irc.error('No definition found.', Raise=True)
        word = definitions[0].word
        definitions = ['%s (%s)' % (d.definition, d.example)
                       for d in definitions]
        reply_msg = '%s: %s' % (word, '; '.join(definitions))
        irc.reply(utils.web.htmlToText(reply_msg.encode('utf8')))
    urbandict = wrap(urbandict, [many('something')])

    def _define(self, irc, getDefinition, license):
        definition = getDefinition(license)
        word = definition.word
        definitions = ['%s (%s)' % (definition.definition, definition.example)]
        irc.reply(utils.web.htmlToText('%s: %s' % (word,
                                                   '; '.join(definitions))))
    def daily(self, irc, msg, args):
        """takes no arguments

        Returns the definition and usage of the daily phrase from
        UrbanDictionary.com.
        """
        license = self._licenseCheck(irc)
        self._define(irc, self.server.get_daily_definition, license)
    daily = wrap(daily)

    def random(self, irc, msg, args):
        """takes no arguments

        Returns the definition and usage of a random phrase from
        UrbanDictionary.com.
        """
        license = self._licenseCheck(irc)
        self._define(irc, self.server.get_random_definition, license)
    random = wrap(random)

Class = UrbanDict


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
