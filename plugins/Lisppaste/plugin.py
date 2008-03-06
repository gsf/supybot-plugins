import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Lisppaste(callbacks.Privmsg):
    def lisppaste(self, irc, msg, args):
        """redirects lisppaste requests to the proper bot
        """
        irc.reply('lisppaste: help [test]', prefixNick=False)

Class = Lisppaste

