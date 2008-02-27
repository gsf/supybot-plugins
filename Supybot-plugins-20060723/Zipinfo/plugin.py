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


class Zipinfo(callbacks.Plugin):
    """Add the help for "@plugin help Zipinfo" here
    This should describe *how* to use this plugin."""
    threaded = True
    def callCommand(self, command, irc, msg, *args, **kwargs):
        try:
            super(Zipinfo, self).callCommand(command,irc,msg,*args,**kwargs)
        except utils.web.Error, e:
            irc.error(str(e))

    _zipinfore = re.compile(r'Latitude<BR>\(([^)]+)\)</th><th>Longitude<BR>'
                            r'\(([^)]+)\).*?<tr>(.*?)</tr>', re.I)
    _zipstatre = re.compile(r'(Only about \d+,\d{3} of.*?in use.)')
    def zipinfo(self, irc, msg, args, zipcode):
        """<zip code>

        Returns a plethora of information for the given <zip code>.
        """
        try:
            int(zipcode)
        except ValueError:
            irc.error('Zip code must be a 5-digit integer.')
            return
        if len(zipcode) != 5:
            irc.error('Zip code must be a 5-digit integer.')
            return
        url = 'http://zipinfo.com/cgi-local/zipsrch.exe?cnty=cnty&ac=ac&'\
              'tz=tz&ll=ll&zip=%s&Go=Go' % zipcode
        text = utils.web.getUrl(url)
        if 'daily usage limit' in text:
            irc.error('I have exceeded the site\'s daily usage limit.')
            return
        m = self._zipstatre.search(text)
        if m:
            irc.reply('%s  %s is not one of them.' % (m.group(1), zipcode))
            return
        n = self._zipinfore.search(text)
        if not n:
            irc.error('Unable to retrieve information for that zip code.')
            return
        (latdir, longdir, rawinfo) = n.groups()
        # Info consists of the following (whitespace separated):
        # City, State Abbrev., Zip Code, County, FIPS Code, Area Code, Time
        # Zone, Daylight Time(?), Latitude, Longitude
        info = utils.web.htmlToText(rawinfo)
        info = info.split()
        zipindex = info.index(zipcode)
        resp = ['City: %s' % ' '.join(info[:zipindex-1]),
                'State: %s' % info[zipindex-1],
                'County: %s' % ' '.join(info[zipindex+1:-6]),
                'Area Code: %s' % info[-5],
                'Time Zone: %s' % info[-4],
                'Daylight Savings: %s' % info[-3],
                'Latitude: %s (%s)' % (info[-2], latdir),
                'Longitude: %s (%s)' % (info[-1], longdir),
               ]
        irc.reply('; '.join(resp))
    zipinfo = wrap(zipinfo, ['text'])


Class = Zipinfo


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
