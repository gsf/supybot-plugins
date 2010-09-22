import json
import urllib

from supybot.commands import wrap, optional
from supybot.callbacks import Plugin

class SocialGraph(Plugin):
    """Flimsy support for Google's Social Graph API.
    """

    def otherme(self, irc, msg, args, uri):
        """Ask google's social graph api about a particular url or email.
        """
        if not uri:
              irc.reply("please supply a URL or email address!")
              return

        profile = self._get_profile()
        irc.reply(', '.join(profile.keys()))

    otherme = wrap(otherme, [optional('text')])

    def _get_profile(self, uri):
        url = "http://socialgraph.apis.google.com/otherme?" + \
            urllib.urlencode({'q': uri})
        return json.loads(urllib.urlopen(url).read())
      
Class = SocialGraph 
