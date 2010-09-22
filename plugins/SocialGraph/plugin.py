import json
import urllib

import supybot.commands
import supybot.callbacks

class SocialGraph(supybot.callbacks.Plugin):
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

    lookup = supybot.commands.wrap(lookup, [optional('text')])

    def _profile(self, uri):
        url = "http://socialgraph.apis.google.com/otherme?" + \
            urllib.urlencode({'q': uri})
        return json.loads(urllib.urlopen(url).read())
      
Class = SocialGraph 
