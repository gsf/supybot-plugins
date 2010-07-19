from urllib import urlencode
from urllib2 import urlopen, HTTPError

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup

def lookup(word):
    from socket import setdefaulttimeout
    setdefaulttimeout(60)
    url = "http://www.etymonline.com/index.php?%s" \
        % urlencode({'search':word, 'searchmode':'or'})

    doc = None
    try:
        doc = urlopen(url)
    except HTTPError, e:
        return 'http error %s for %s' % (e.code, url)

    soup =  BeautifulSoup(doc)
    dd = soup.find('dd', 'highlight')

    if dd: 
        etym = u''
        for part in dd:
            try:
                etym += part.string
            except:
                pass
        return etym.strip()
    else:
        return "%s not found" % word

class Etymology(callbacks.Privmsg):

    def etym(self,irc,msg,args):
        """etym <word> lookup the etymology for a word/phrase
        """
        etymology = lookup(''.join(args))
        irc.reply(etymology.encode('utf-8'))

Class = Etymology 

