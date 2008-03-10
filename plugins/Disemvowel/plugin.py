import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re

class Disemvowel(callbacks.Privmsg):
    def disemvowel(self, irc, msg, args):
        """removes vowels from strings
        """
        irc.reply(re.sub(r'[AEIOUYaeiouy]', '', ' '.join(args)), prefixNick=True)

Class = Disemvowel

