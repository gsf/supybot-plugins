from urllib import quote
from urllib2 import urlopen, Request
import re

import supybot.callbacks as callbacks

class Solr(callbacks.Privmsg):

    def grep(self,irc,msg,args):
        """search bartleby's memory
        """
        args.append('; timestamp desc')
        q = quote(' '.join(args))
        conn = urlopen('http://localhost:9001/solr/select?q=%s&wt=python' % q)
        response = eval(conn.read())
        hits = []
        for doc in response['response']['docs']:
            if doc.has_key('url'):
              hits.append("%s: %s <%s>" % (doc['nick'], doc['message'], doc['url']))
            else:
              hits.append("%s: %s" % (doc['nick'], doc['message']))
        if len(hits) > 0:
          irc.reply('grep found: ' + ' ; '.join(hits).encode('utf8','ignore'), 
              prefixNick=False)
        else:
          irc.reply('grep found: nada, nothin, zilch, zero', prefixNick=False)

Class = Solr
