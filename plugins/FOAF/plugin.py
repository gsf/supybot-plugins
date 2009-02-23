import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re
import os
import shutil
from rdflib import ConjunctiveGraph as Graph
from rdflib import Namespace
from rdflib import URIRef
from rdflib import Literal
import rdflib


class FOAF(callbacks.Privmsg):
  
    def __init__(self, irc):
      self.g = Graph()
      self.g.parse('/var/www/rc98.net/zoia.rdf', format="xml")
      self.uri = rdflib.URIRef('http://www.code4lib.org/id/zoia')
      self.FOAF = Namespace('http://xmlns.com/foaf/0.1/')
      super(callbacks.Plugin,self).__init__(irc)
      

    def knows(self, irc, msg, args):
      usernick1 = args[0]
      usernick2 = args[0]
      result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri1 ?uri2 WHERE {<http://www.code4lib.org/id/zoia> foaf:knows ?uri . ?uri1 foaf:nick ?nick1 . ?uri2 foaf:nick ?nick2}', initBindings={'?nick1': usernick1, '?nick2': usernick2} )
      
    def known(self, irc, msg, args):
      if len(args) == 1:
        usernick = args[0]
      else:
        irc.reply("Usage: @known [nick]")
        return
      result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri WHERE {<http://www.code4lib.org/id/zoia> foaf:knows ?uri . ?uri foaf:nick ?nick .}', initBindings={'?nick': usernick} )
      if len(result) > 0:
        userURI = list(result)[0][0].__str__()
        irc.reply(usernick+"'s URI is <"+userURI+">", prefixNick=True)
      else:
        irc.reply("I don't know "+usernick+"'s URI")
        
    def know(self, irc, msg, args):
      if len(args) == 1:
        uri = args[0]
      else:
        irc.reply("Usage: @know [URI]")
        return
      FOAF = self.FOAF
      user = rdflib.URIRef(uri)
      self.g.add((user, rdflib.RDF.type, FOAF['Person']))
      self.g.add((user, FOAF['nick'], rdflib.Literal(msg.nick)))
      self.g.add((self.uri, FOAF['knows'], user))
      
      self.g.serialize('/var/www/rc98.net/zoia.rdf')
      
    def reloadfoaf(self, irc, msg, args):
      originalFOAF = 'supybot-plugins/plugins/foaf.rdf'
      liveFOAF = '/var/www/rc98.net/zoia.rdf'
      shutil.copyfile(originalFOAF, liveFOAF)
      irc.reply('File copied')
      

Class = FOAF

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
