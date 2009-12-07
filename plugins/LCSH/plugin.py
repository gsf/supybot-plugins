from supybot.commands import *
import supybot.callbacks as callbacks

from urllib import urlencode, urlopen
from socket import setdefaulttimeout

class LCSH(callbacks.Privmsg):

    def lcsh(self, irc, msg, args):
        """lcsh search for headings
        """
        heading = ' '.join(args)
        headings = self._do_search(heading)
        results = map(lambda r: "%s <%s>" % (r['pref_label'], r['url']), 
                      headings)
        if not results:
            irc.reply('sorry no hits for %s, email Sandy Berman' % heading)
        else:
            irc.reply('; '.join(results).encode('utf-8'))

    def _do_search(self, heading):
        setdefaulttimeout(60)
        url = 'http://id.loc.gov/authorities/search?' + \
               urlencode({'q': heading, 'format': 'json'})
        return simplejson.loads(urlopen(url).read())

Class = LCSH
