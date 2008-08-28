import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re

class Translators(callbacks.Privmsg):
    def canuck(self, irc, msg, args):
        """translates text into a Canadian dialect
        """
        text = ' '.join(args)
        text = re.sub(r'out', 'oat', text)
        text = re.sub(r'ouch', 'oach', text)
        text = re.sub(r'ache', 'awchee', text)
        irc.reply(text + "  eh?", prefixNick=True)

    def mccainize(self, irc, msg, args):
        """translates text into McCain speechifyin'
        """
        irc.reply(re.sub(r'^', 'my friends, ', ' '.join(args)), prefixNick=True)

    def dick (self, irc, msg, args):
        """disclaims your desire to be a dick
        """
        irc.reply("I don't mean to be a dick, but " + ' '.join(args), prefixNick=True)
        
Class = Translators

