from opensearch import Client

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class OpenSearch(callbacks.Privmsg):
    """add an opensearch target: add <alias> <description_url>
    """

    def add(self,irc,msg,args):

        if not hasattr(self,'opensearch_clients'):
            self.opensearch_clients = {}

        try:
            alias, description_url = args
        except:
            irc.reply("please try: add <alias> <description_url>")

        try:
            client = Client(description_url)
            self.make_search_method(alias,client)
            irc.reply("added opensearch server %s with alias %s" %
                    (client.description.shortname.encode('utf8','ignore'), alias))
        except Exception, e:
            self.log.error(str(e))
            irc.reply("unable to load opensearch description")


    def servers(self,irc,msg,args):
        """lists configured opensearch servers
        """
        if hasattr(self,'opensearch_clients') \
            and len(self.opensearch_clients) > 0:
            irc.reply( "configured servers: " + \
                ','.join(self.opensearch_clients.keys()) )
        else:
            irc.reply("no servers set up") 

    def make_search_method(self,alias,client):
        self.opensearch_clients[alias] = client

        def f (self,irc,msg,args):
            from socket import setdefaulttimeout
            setdefaulttimeout(60)
            query = ' '.join(args)
            results = client.search(query)
            count = 0
            response = ""
            for r in results:
                if hasattr(r, 'title'):
                    response += r.title.encode('ascii', 'ignore')
                if hasattr(r, 'link'):
                    response += " " + r.link.encode('ascii', 'ignore')
                response += " ; "
                count += 1
                if count > 5:
                    break
            if count > 0:
                irc.reply(response)
            else:
                irc.reply("no hits (right now) for %s" % query)

        setattr(self.__class__, alias, f)

Class = OpenSearch

