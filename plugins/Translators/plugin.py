import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re
from random import randint

class Translators(callbacks.Privmsg):
    def canuck(self, irc, msg, args):
        """
        Translates text into a Canadian dialect
        """
        text = ' '.join(args)
        text = re.sub(r'out', 'oat', text)
        text = re.sub(r'ouch', 'oach', text)
        text = re.sub(r'ache', 'awchee', text)
        irc.reply(text + ", eh?", prefixNick=True)

    def mccainize(self, irc, msg, args):
        """
        Translates text into McCain speechifyin'
        """
        irc.reply('my friends, ' + ' '.join(args), prefixNick=True)

    def dick(self, irc, msg, args):
        """
        Disclaims your desire to be a dick
        """
        irc.reply("I don't mean to be a dick, but " + ' '.join(args), prefixNick=True)
        
    def edsu(self, irc, msg, args):
        """
        States edsu's attitude on selfsame plugin command
        """
        irc.reply("edsu finds this supremely annoying, but " + ' '.join(args), prefixNick=True)

    def obamit(self, irc, msg, args):
        """
        Garners attention for your statements in a folksy way
        """
        look = "Look, "
        if randint(0,1): look = "Look, here's what I'm saying... "
        irc.reply(look + ' '.join(args))

    def mjg(self, irc, msg, args):
        """
        Truncates and refocuses your statement
        """
        s = ' '.join(args)
        low = 10
        high = len(s) - 10
        if len(s) < low:
            low = len(s)
        irc.reply("%s... OMG! Bacon!" % s[:randint(low,high)])

        
Class = Translators

