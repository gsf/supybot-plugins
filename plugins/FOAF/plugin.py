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
        
    def foaf(self, irc, msg, args):
        if len(args) > 1:
          if args[0] == 'knows':
            usernick1 = args[1]
            usernick2 = args[2]
            result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri1 ?uri2 WHERE {<http://www.code4lib.org/id/zoia> foaf:knows ?uri . ?uri1 foaf:nick ?nick1 . ?uri2 foaf:nick ?nick2}', initBindings={'?nick1': usernick1, '?nick2': usernick2} )
    def known(self, irc, msg, args):
      usernick = args[0]
      result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri WHERE {<http://www.code4lib.org/id/zoia> foaf:knows ?uri . ?uri foaf:nick ?nick}', initBindings={'?nick': usernick} )
      if len(result) > 0:
        userURI = list(result)[0][0].__str__()
        irc.reply(usernick+"'s URI is <"+userURI+">", prefixNick=True)
      else:
        irc.reply("I don't know "+args[1]+"'s URI")

Class = FOAF

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
