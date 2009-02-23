import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re
from rdflib import ConjunctiveGraph as Graph
from rdflib import Namespace
from rdflib import URIRef
from rdflib import Literal


class FOAF(callbacks.Privmsg):
  
    def __init__(self, irc):
        self.g = Graph()
        self.g.parse('http://rc98.net/zoia.rdf', format="xml")
        super(callbacks.Plugin,self).__init__(irc)
        
    def foaf(self, irc, msg, args, url):
        """
        <url>: 
        """
        if len(args) > 1:
          if args[0] == 'knows':
            pass
          elif args[0] == 'known':
            result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri WHERE {<http://www.code4lib.org/id/zoia> foaf:knows ?uri . ?uri foaf:nick ?nick}', initBindings={'?nick': args[1]} )
            if len(result) > 0:
              userURI = list(result)[0][0].__str__()
              irc.reply(args[1]+"'s URI is <"+userURI+">", prefixNick=True)
            else:
              irc.reply("I don't know "+args[1]+"'s URI")

Class = FOAF

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
