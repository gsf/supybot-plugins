from urllib import quote
from urllib2 import urlopen, Request
import re

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class BlogWorth(callbacks.Privmsg):

    def worth(self,irc,msg,args):
        """look up the worth of a url
        """
        url = ''.join(args)
        url = "http://www.business-opportunities.biz/projects/how-much-is-your-blog-worth/?url="+quote(url)
        request = Request(url, None, {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'})
        html = urlopen(request).read()
        m = re.match(".*(\$[0-9.,]+).*", html, re.DOTALL)
        worth = "$0.00"
        if m: worth = m.group(1)
        irc.reply(worth)

Class = BlogWorth
