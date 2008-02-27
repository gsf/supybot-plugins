from urllib import urlencode
from urllib2 import urlopen 
from elementtidy import TidyHTMLTreeBuilder

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

def lookup(word):
    from socket import setdefaulttimeout
    setdefaulttimeout(60)
    url = "http://www.etymonline.com/index.php?%s" \
        % urlencode({'search':word})
    tree = TidyHTMLTreeBuilder.parse(urlopen(url))
    dd = tree.find('.//{http://www.w3.org/1999/xhtml}dd')
    if dd: 
        return textify(dd)
    else:
        return "%s not found" % word

def textify(e):
    text = ""
    if e.text:
        text = e.text 
    if e.tail: 
        text += e.tail
    for c in e:
        text += textify(c)
    return text.replace("\n","")

class Etymology(callbacks.Privmsg):

    def etym(self,irc,msg,args):
        """etym <word> lookup the etymology for a word/phrase
        """
        etymology = lookup(''.join(args))
        irc.reply(etymology.encode('utf8', 'ignore'))

Class = Etymology 

