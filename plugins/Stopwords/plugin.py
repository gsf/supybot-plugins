from supybot.commands import *
import supybot.callbacks as callbacks

from urllib2 import build_opener
from random import randint

class Stopwords(callbacks.Privmsg):
    def stopwords(self,irc,msg,args):
        """stopwords

        Get a stopword from ICAP's list
        """

        url = "https://svn.library.oregonstate.edu/repos/ica/tags/ica_0.9/lib/words.txt"
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        text = opener.open(url).read()
        words = text.split()
        word = words[randint(0,len(words)-1)]
        irc.reply(word, prefixNick=True)

Class = Stopwords
