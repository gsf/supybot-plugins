from urllib import quote
from urllib2 import urlopen, Request

import supybot.callbacks as callbacks

class Delicious(callbacks.Privmsg):

    def fauxonomy(self,irc,msg,args):
        """get tags associated with a url
        """
        url = quote(args[0])
        conn = urlopen('http://badges.del.icio.us/feeds/json/url/data?url=%s' 
            % url)
        response = eval(conn.read())
        if len(response) == 0:
          irc.reply("site doesn't appear to be in delicious")
          return
        total_posts = response[0]['total_posts']
        tag_stats = response[0]['top_tags']
        tags = tag_stats.keys()
        tags.sort(lambda a,b: cmp(tag_stats[b], tag_stats[a]))
        msg = ' ; '.join(map(lambda tag: "%s:%i" % (tag, tag_stats[tag]), tags))
        irc.reply("[%i posts] %s" % (total_posts, msg))

Class = Delicious
