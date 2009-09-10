import supybot.utils as utils
import supybot.utils.web as web
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import simplejson

API_URL = 'http://genderednames.freebaseapps.com/gender_api?name=%s'
HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Gender Plugin; http://code4lib.org/irc)')

def percentage(dividend, divisor):
    """ formats a percentage calculated from two ints """
    return str((float(dividend) / float(divisor)) * 100)[:4]


class Gender(callbacks.Plugin):
    threaded = True

    def gender(self, irc, msg, args, name):
        """<name>
        
        Returns gender data on name usage from Freebase:
        http://genderednames.freebaseapps.com/
        """

        url = API_URL % name
        json = web.getUrl(url, headers=HEADERS)
        response = simplejson.loads(json)

        if not response['total']:
            irc.reply("The name '%s' was not found on Freebase" % name)
            return

        female_percentage = percentage(response['female'], response['total'])
        male_percentage = percentage(response['male'], response['total'])
        irc.reply("'%s': %s%% female; %s%% male (%s)" % (name, female_percentage, male_percentage, response), prefixNick=True)

    gender = wrap(gender, ['text'])
        

Class = Gender

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
