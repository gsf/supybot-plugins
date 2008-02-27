###
# Copyright (c) 2003-2005, James Vega
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
import cgi

import supybot.utils as utils
from supybot.commands import *
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class EbayError(Exception):
    pass

class Ebay(callbacks.PluginRegexp):
    """Add the help for "@help Ebay" here (assuming you don't implement a Ebay
    command).  This should describe *how* to use this plugin."""
    threaded = True
    callBefore = ['Web']
    regexps = ['ebaySnarfer']

    _reopts = re.I | re.S
    _invalid = re.compile(r'(is invalid, still pending, or no longer in our '
                          r'database|has been removed by eBay)', _reopts)
    _info = re.compile(r'<title>eBay:\s+(.*?)\s+\(item (\d+)[^)]+\)</title>',
                       _reopts)

    _bid = re.compile(r'((?:Current|Starting) bid):.+?<b>([^<]+?)<', _reopts)
    _winningBid = re.compile(r'(Winning bid|Sold for):.+?<b>([^<]+?)</b',
                             _reopts)
    _time = re.compile(r'(Time left):.+?<b>([^<]+?)</b>', _reopts)
    _bidder = re.compile(r'(High bidder):.+?(?:">(User ID) (kept private)'
                         r'</font>|<a href[^>]+>([^<]+)</a>.+?'
                         r'<a href[^>]+>(\d+)</a>)', _reopts)
    _winningBidder = re.compile(r'(Winning bidder|Buyer):.+?<a href[^>]+>'
                               r'([^<]+)</a>.+?<a href[^>]+>(\d+)</a>',_reopts)
    _buyNow = re.compile(r'alt="(Buy It Now)">.*?<b>([^<]+)</b>', _reopts)
    _seller = re.compile(r'(Seller information).+?<a href[^>]+>([^<]+)</a>'
                         r'.+ViewFeedback.+">(\d+)</a>', _reopts)
    _searches = (_bid, _winningBid, _time, _bidder,
                 _winningBidder, _buyNow, _seller)
    _multiField = (_bidder, _winningBidder, _seller)

    def auction(self, irc, msg, args, item):
        """<item>

        Return useful information about the eBay auction with item number
        <item>.
        """
        url = 'http://cgi.ebay.com/ws/eBayISAPI.dll?ViewItem&item=%s' % item
        try:
            irc.reply(format('%s %u', self._getResponse(url), url))
        except EbayError, e:
            irc.error(str(e))
    auction = wrap(auction, [('id', 'auction')])

    def ebaySnarfer(self, irc, msg, match):
        r'http://cgi\.ebay\.(?:com(?:\.au)?|co\.uk|ca)/.*' \
        r'eBayISAPI\.dll\?ViewItem&([\S]+)'
        if not self.registryValue('auctionSnarfer', msg.args[0]):
            return
        queries = cgi.parse_qs(match.group(1))
        L = map(str.lower, queries.keys())
        if 'item' not in L and 'category' not in L:
            return
        url = match.group(0)
        try:
            irc.reply(self._getResponse(url), prefixNick=False)
        except EbayError, e:
            self.log.info('ebaySnarfer exception at %u: %s', url, str(e))
    ebaySnarfer = urlSnarfer(ebaySnarfer)

    def _getResponse(self, url):
        def bold(L):
            return (ircutils.bold(L[0]),) + L[1:]
        try:
            s = utils.web.getUrl(url)
        except utils.web.Error, e:
            raise EbayError, str(e)
        resp = []
        m = self._invalid.search(s)
        if m:
            raise EbayError, format('That auction %s.', m.group(1))
        m = self._info.search(s)
        if m:
            (desc, num) = map(str.strip, m.groups())
            resp.append(format('%s%s: %s',
                               ircutils.bold('Item #'),
                               ircutils.bold(num), desc))
        for r in self._searches:
            m = r.search(s)
            if m:
                if r in self._multiField:
                    # Have to filter the results from self._bidder since
                    # 2 of the 5 items in its tuple will always be None.
                    #self.log.warning(m.groups())
                    matches = filter(None, m.groups())
                    matches = tuple(map(str.strip, matches))
                    resp.append(format('%s: %s (%s)', *bold(matches)))
                else:
                    matches = tuple(map(str.strip, m.groups()))
                    resp.append(format('%s: %s', *bold(matches)))
        if resp:
            return utils.web.htmlToText('; '.join(resp))
        else:
            raise EbayError, format('That doesn\'t appear to be a proper eBay '
                                    'auction page.  (%s)',
                                    conf.supybot.replies.possibleBug())


Class = Ebay


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
