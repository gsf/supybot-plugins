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

import re

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class AcronymFinder(callbacks.Plugin):
    """Add the help for "@plugin help AcronymFinder" here
    This should describe *how* to use this plugin."""
    threaded = True
    def callCommand(self, command, irc, msg, *args, **kwargs):
        try:
            parent = super(AcronymFinder, self)
            parent.callCommand(command, irc, msg, *args, **kwargs)
        except utils.web.Error, e:
            irc.error(str(e))

    _acronymre = re.compile(r"(?P<result>.*)\s\[.*<a href='(?P<url>.*)'>"
                            r"(?P<number>\d*)", re.I | re.M)
    def acronym(self, irc, msg, args, acronym, token):
        """<acronym> [<token>]

        Displays the top acronym match from acronymfinder.com.

        <token> is an optional argument that, when supplied, will limit the
        response to only those answers containing that word.
        """
        licenseKey = self.registryValue('licenseKey')
        if not licenseKey:
            irc.error('You must have a free Acronym Finder license key '
                      'in order to use this command.  You can get one at '
                      '<http://www.acronymfinder.com/dontknowyet/>.  Once you '
                      'have one, you can set it with the command '
                      '"config supybot.plugins.Acronym.licenseKey <key>".')
            return
        if token:
            url = 'http://www.acronymfinder.com/' \
                'TopAcronym.aspx?key=%s&q=%s&token=%s' \
                % (licenseKey, acronym, token)
        else:
            url = 'http://www.acronymfinder.com/' \
                'TopAcronym.aspx?key=%s&q=%s' % (licenseKey, acronym)
        html = utils.web.getUrl(url)
        matchobj = self._acronymre.search(html)
        if 'daily limit' in html:
            s = 'Acronymfinder.com says I\'ve reached my daily limit.  Sorry.'
            irc.error(s)
            return
        if not matchobj:
            irc.reply('No definitions found.')
        else:
            groups = matchobj.groupdict()
            s = "Acronym Finder Says: '%s'" % groups['result']
            if int(groups.get('number', 0)) > 0:
                s = "%s -- %s More Definitions At <%s>" \
                % (s, groups['number'], groups['url'])
            irc.reply(s)
    acronym = wrap(acronym, ['something', additional('something')])


Class = AcronymFinder


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
