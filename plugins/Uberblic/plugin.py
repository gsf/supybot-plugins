
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import urllib2
import simplejson

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Uberblic Plugin; http://code4lib.org/irc)')
SERVICE_URL = 'http://platform.uberblic.org/api/search?query=%s'

class Uberblic(callbacks.Plugin):
    """Add the help for "@plugin help Uberblic" here
    This should describe *how* to use this plugin."""
    threaded = True

    def uberblic(self, irc, msg, args, query):
        """[<query>]

        uses the uberblic.org search api to return
        descriptions for a query term or terms
        """
        url = SERVICE_URL % urllib2.quote(query)
        u = urllib2.urlopen(url)
        json = simplejson.load(u)

        result_count = len(json['results'])
        if result_count:
            desc = json['results'][0]['description']
            irc.reply(desc.encode('utf-8'))
        else:
            irc.reply('No results. Better luck next time')

    uberblic = wrap(uberblic, ['text'])


Class = Uberblic


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
