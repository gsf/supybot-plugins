import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re
from random import randint
import supybot.utils.web as web
from urllib import urlencode

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Sing Plugin; http://code4lib.org/irc)')

class Translators(callbacks.Privmsg):
    def canuck(self, irc, msg, args):
        """ string
        Translates text into a Canadian dialect
        """
        text = ' '.join(args)
        text = re.sub(r'out', 'oat', text)
        text = re.sub(r'ouch', 'oach', text)
        text = re.sub(r'ache', 'awchee', text)
        matches = re.findall(r'((-?\d+)(\.\d+)?.F)', text)
        for match in matches:
            ftemp = float(match[1] + match[2])
            celsius = "%-3.2f" % ((ftemp - 32) * 5 / 9)
            text = re.sub(match[0], str(celsius) + 'C', text)
        irc.reply(text + ", eh?", prefixNick=True)

    def aussie(self, irc, msg, args):
        """ string
        Translates string into Australian English Vernacular
        """
        irc.reply("SHRIMP ON THE BARBIE, MATES!", prefixNick=True)

    def ircnickize(self, irc, msg, args):
        """ string
        Normalizes a string per irc nick rules
        """
        nick = ''
        for arg in args:
            for s in arg.split():
                nick += s
        # strip out all non-word characters to make freenode happy
        nick = re.compile(r'\W', re.I).sub('', nick)        
        # string slice used because freenode restricts >16-char nicks
        irc.reply(nick[0:15], prefixNick=False)

    def mccainize(self, irc, msg, args):
        """
        Translates text into McCain speechifyin'
        """
        prefix = "My friends, " if randint(0,2) else "My fellow prisoners, "
        irc.reply(prefix + ' '.join(args), prefixNick=True)

    def dick(self, irc, msg, args):
        """
        Disclaims your desire to be a dick
        """
        irc.reply("I don't mean to be a dick, but " + ' '.join(args), prefixNick=True)
        
    def edsu(self, irc, msg, args):
        """
        States edsu's attitude on selfsame plugin command
        """
        irc.reply("let me remind you people, " + ' '.join(args), prefixNick=True)

    def kgs(self, irc, msg, args):
        """
        bad kgs imitation
        """
        irc.reply("nosrsly, " + ' '.join(args), prefixNick=True)


    def obamit(self, irc, msg, args):
        """
        Garners attention for your statements in a folksy way
        """
        look = "Look, " if randint(0,1) else "Look, here's what I'm saying... "
        irc.reply(look + ' '.join(args))

    def mjg(self, irc, msg, args):
        """
        Truncates and refocuses your statement
        """
        s = ' '.join(args)
        high = len(s)
        low = min(7, high-1)
        irc.reply("%s... OMG! Bacon!" % s[0:randint(low,high)])

    def embed(self, irc, msg, args):
        """
        Adds "in bed" to the end of a phrase.
        """
        s = ' '.join(args).strip(".")

        motivate = re.match(r'^(.*) - (.*)$', s)
        quote = re.match(r'^Quote #(\d+): "(.*)" \((.*)\)$', s)
        if motivate:
            msg = "%s ... in bed - %s" % (motivate.group(1), motivate.group(2))
        elif quote:
            msg = 'Quote #%sa "%s ... in bed" - (%s)' % quote.groups()
        else:
            msg = "%s ... in bed." % s

        irc.reply(msg)

    def chef(self, irc, msg, args):
        """BORK! BORK! BORK!"""
        self._chefjivevalleypig(irc, 'chef', ' '.join(args))

    def jive(self, irc, msg, args):
        """Like, yeah..."""
        self._chefjivevalleypig(irc, 'jive', ' '.join(args))

    def valley(self, irc, msg, args):
        """Fer sure!"""
        self._chefjivevalleypig(irc, 'valspeak', ' '.join(args))

    def igpay(self, irc, msg, args):
        """Ustjay utwhay ouyay inkthay"""
        self._chefjivevalleypig(irc, 'piglatin', ' '.join(args))

    def _chefjivevalleypig(self, irc, type, s):
        params = urlencode(dict(input=s,type=type))
        url = 'http://www.cs.utexas.edu/users/jbc/bork/bork.cgi?' + params
        resp = web.getUrl(url, headers=HEADERS)
        irc.reply(resp.encode('utf-8', 'ignore').strip())
        
Class = Translators

