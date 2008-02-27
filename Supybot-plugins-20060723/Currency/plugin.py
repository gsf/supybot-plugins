###
# Copyright (c) 2004-2005, James Vega
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
import supybot.callbacks as callbacks


class Currency(callbacks.Privmsg):
    threaded = True
    currencyCommands = ['xe', 'yahoo']
    _symbolError = 'Currency must be denoted by its three-letter symbol.'
    def convert(self, irc, msg, args):
        """[<number>] <currency1> [to] <currency2>

        Converts from <currency1> to <currency2>.  If number isn't given, it
        defaults to 1.
        """
        channel = None
        if irc.isChannel(msg.args[0]):
            channel = msg.args[0]
        realCommandName = self.registryValue('command', channel)
        realCommand = getattr(self, realCommandName)
        realCommand(irc, msg, args)

    _xeCurrError = re.compile(r'The following error occurred:<BR><BR>\s+'
                              r'(.*)</body>', re.I | re.S)
    _xeConvert = re.compile(r'<span style[^>]+>([\d.]+\s+\w{3})<', re.I | re.S)
    def xe(self, irc, msg, args, number, curr1, curr2):
        """[<number>] <currency1> [to] <currency2>

        Converts from <currency1> to <currency2>.  If number isn't given, it
        defaults to 1.
        """
        if len(curr1) != 3 and len(curr2) != 3:
            irc.error(self._symbolError, Raise=True)
        url = 'http://www.xe.com/ucc/convert.cgi?Amount=%s&From=%s&To=%s'
        try:
            text = utils.web.getUrl(url % (number, curr1, curr2))
        except utils.web.Error, e:
            irc.error(str(e), Raise=True)
        err = self._xeCurrError.search(text)
        if err is not None:
            irc.error('You used an incorrect currency symbol.', Raise=True)
        resp = []
        m = self._xeConvert.finditer(text)
        for conv in m:
            L = conv.group(1).split()
            s = str(float(L[0]))
            if s.endswith('.0'):
                s = s[:-2] + '.00'
            L[0] = s
            resp.append(' '.join(L))
        if len(resp) == 2:
            irc.reply(format('%s = %s', resp[0], resp[1]))
        else:
            irc.error('XE must\'ve changed the format of their site.',
                      Raise=True)
    xe = wrap(xe, [optional('float', 1.0), 'lowered', 'to', 'lowered'])

    def yahoo(self, irc, msg, args, number, curr1, curr2):
        """[<number>] <currency1> to <currency2>

        Converts from <currency1> to <currency2>.  If number isn't given, it
        defaults to 1.
        """
        if len(curr1) != 3 and len(curr2) != 3:
            irc.error(self._symbolError, Raise=True)
        url = r'http://finance.yahoo.com/d/quotes.csv?'\
              r's=%s%s=X&f=sl1d1t1ba&e=.csv' % (curr1, curr2)
        try:
            text = utils.web.getUrl(url)
        except utils.web.Error, e:
            irc.error(str(e), Raise=True)
        if 'N/A' in text:
            irc.error('You used an incorrect currency symbol.', Raise=True)
        conv = text.split(',')[1]
        conv = number * float(conv)
        irc.reply(format('%.2f %s = %.2f %s', number, curr1, conv, curr2))
    yahoo = wrap(yahoo, [optional('float', 1.0), 'lowered', 'to', 'lowered'])


Class = Currency


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
