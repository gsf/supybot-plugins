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

    def ircnickize(self, irc, msg, args):
        """ string
        Normalizes a string per irc nick rules
        """
        nick = '_'.join(args)
        irc.reply("args: %s ;  msg: %s" % (args, msg), prefixNick=False)
        #irc.reply(nick, prefixNick=False)

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
        if motivate:
            msg = "%s ... in bed - %s" % (motivate.group(1), motivate.group(2))
        else:
            msg = "%s ... in bed." % s

        irc.reply(msg)
        
Class = Translators

