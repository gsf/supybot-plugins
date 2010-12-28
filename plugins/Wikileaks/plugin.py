
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
import urllib
import re
import copy
from urllib2 import Request, build_opener, HTTPError
from string import capwords
from random import randint

class Wikileaks(callbacks.Plugin):
    """Add the help for "@plugin help Wikileaks" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self,irc):
        self.__parent = super(Wikileaks, self)
        self.__parent.__init__(irc)
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        self.opener = build_opener()
        self.opener.addheaders = [('User-Agent', ua)]
        
    def whyiswikileaksagoodthing(self, irc, msg, args):
        """
        So why is WikiLeaks a Good Thing Again?
        """
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open('http://sowhyiswikileaksagoodthingagain.com/')
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        results = soup.find('div', {'class': 'what'}).next
        out = results.strip()
        irc.reply(out.encode('utf-8'), prefixNick=True)

Class = Wikileaks

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
