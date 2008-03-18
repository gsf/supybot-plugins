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
        irc.reply(re.sub(r'out(\b)', 'oot', text) + " eh?", prefixNick=True)

Class = Translators

