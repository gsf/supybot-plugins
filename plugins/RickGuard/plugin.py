
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from urllib2 import urlopen, urlparse, Request, build_opener, HTTPError
from urlparse import urlparse
import re
import time

class RickGuard(callbacks.PluginRegexp):
    """Add the help for "@plugin help RickGuard" here
    This should describe *how* to use this plugin."""

    regexps = ['rollcheck']

    def __init__(self,irc):
        self.__parent = super(RickGuard, self)
        self.__parent.__init__(irc)
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        self.opener = build_opener()
        self.opener.addheaders = [('User-Agent', ua)]

    def rollcheck(self,irc,msg,match):
#        r"(https?)://[-\w]+(\.\w[-\w]*)+(:[\d]{1,5})?[^\s]*"
        r"(?rickcheck.+)(https?)://[-\w]+(\.\w[-\w]*)+(:[\d]{1,5})?((/?\w+/?)+|/?)(\w+\.[\w]{3,4})?((\?\w+(=\w+)?)(&\w+(=\w+)?)*)?"
        url = match.group(1)

        parsed = urlparse(url)
        if parsed.hostname.find('youtube') != -1:
            return

        f = None
        try:
            f = self.opener.open(url)
        except HTTPError,e:
            return

        parsed = urlparse(f.geturl())
        if parsed.hostname.find('youtube') != -1:
            irc.reply("Warning: possible RickRoll attempt!", prefixNick=False)

Class = RickGuard
