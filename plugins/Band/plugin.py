###
# Copyright (c) 2008, Michael B. Klein
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
from urllib import urlencode
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup, SoupStrainer
from random import randint


class Band(callbacks.Plugin):
    """
    Generates a random band name."""
    pass

    def band(self, irc, msg, args):
        pages = "a b c d e f g h i j k l m n o p q r s t u v w x y z misc".split(' ')
        url = "http://www.amiright.com/names/cool/" + pages[randint(0,len(pages)-1)] + ".shtml"
        response = urlopen(url)
        soup = BeautifulSoup(response, convertEntities='html')

        try:
            possibles = soup.findAll('p',{'style':True})[0].findAll('a')
            other_url = possibles[randint(0,len(possibles)-1)]['href']
        except:
            other_url = url

        if other_url != url:
            response = urlopen(other_url)
            soup = BeautifulSoup(response, convertEntities='html')

        names = soup.findAll('b')
        name = names[randint(0,len(names)-1)].string

        irc.reply(name.encode('utf8'), prefixNick=True)
        

Class = Band


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
