import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import NACO as oclcnaco

class NACO(callbacks.Privmsg):
    def naco(self, irc, msg, args, url):
        """
        Normalize text according to NACO normalization rules (http://www.loc.gov/catdir/pcc/naco/normrule.html)

        Thanks to OCLC for naco.py.
        """
        try:
            response = oclcnaco.normalize(text)
            irc.reply(response, prefixNick=True)
        except:
            irc.reply("Man, I have no idea; things blew up real good.", prefixNick=True)
    naco = wrap(naco, ['text'])

Class = NACO

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
