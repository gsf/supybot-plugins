import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
import urllib
import urllib2

class Levenshtein(callbacks.Privmsg):
    def levenshtein(self, irc, msg, args):
        """<string> <string>

        Calculates the levenshtein distance between any two strings
        """
        if len(args) != 2:
            irc.reply("usage: levenshtein <string> <string>", prefixNick=True)
            return
        url = 'http://gtools.org/levenshtein-calculate.php'
        values = {
            'str1': args[0],
            'str2': args[1],
        }
        data = urllib.urlencode(values)
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request).read()
        soup = BeautifulSoup(response)
        answer = soup.form.nextSibling.nextSibling.contents

        irc.reply(answer, prefixNick=True)

Class = Levenshtein

