from urllib import urlencode
from urllib2 import urlopen 
from elementtidy import TidyHTMLTreeBuilder

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Euphemism(callbacks.Privmsg):

    def euph(self, irc, msg, args):
        """generate a euphemism
        """
        url = "http://walkingdead.net/perl/euphemism"
        tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        ns = 'http://www.w3.org/1999/xhtml'
        td = tree.find('.//{%(ns)s}table/{%(ns)s}tr/{%(ns)s}td' % {'ns':ns})
        if td:
            irc.reply("%s ... %s" % (td.text, td.find('.//{%s}h2' % ns).text))
        else:
            irc.reply("uhoh, couldn't get a euphemism, sorry dude")

Class = Euphemism

