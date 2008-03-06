import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Lisppaste(callbacks.Privmsg):
    def lisppaste(self, irc, msg, args):
        """redirects lisppaste requests to the proper bot
        """
        irc.reply('lisppaste: help', prefixNick=False)

    def lptest(self, irc, msg, args, otherarg):
        """is a big dumb test
        """
        irc.reply("args are %s; otherarg is %s" % (args, otherarg))

Class = Lisppaste

