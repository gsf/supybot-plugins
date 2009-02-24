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
      elif len(args) == 0:
        usernick = msg.nick
      else:
        irc.reply("Usage: @known [nick (optional)]")
        return
      result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri WHERE {<http://www.code4lib.org/id/zoia> foaf:knows ?uri . ?uri foaf:nick ?nick .}', initBindings={'?nick': usernick} )
      if len(result) > 0:
        userURI = list(result)[0][0].__str__()
        irc.reply(usernick+"'s URI is <"+userURI+">", prefixNick=True)
      else:
        irc.reply("I don't know "+usernick+"'s URI")
        
    def know(self, irc, msg, args):
      if len(args) == 2:
        usernick = args[0]
        userURI = rdflib.URIRef(args[1])
        uristring = args[1]
      elif len(args) == 1:
        usernick = msg.nick
        userURI = rdflib.URIRef(args[0])
        uristring = args[0]
      else:
        irc.reply("Usage: @know [nick (optional)] [URI]")
        return
      FOAF = self.FOAF
      
      result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri WHERE {?uri foaf:nick ?nick .}', initBindings={'?nick': usernick} )
      
      if len(result) > 0:
        irc.reply('about to remove nick')
        self.g.remove(userURI, FOAF['nick'], rdflib.Literal(usernick))
        irc.reply('about to remove type')
        self.g.remove(userURI, rdflib.RDF.type, FOAF['person'])
        irc.reply('about to remove knows')
        self.g.remove(self.uri, FOAF['knows'], userURI)
        irc.reply('everything removed')
      
      self.g.add((userURI, rdflib.RDF.type, FOAF['Person']))
      self.g.add((userURI, FOAF['nick'], rdflib.Literal(usernick)))
      self.g.add((self.uri, FOAF['knows'], userURI))
      
      self.g.serialize('/var/www/rc98.net/zoia.rdf')
      irc.reply('Your URI is now <'+uristring+'>', prefixNick=True)
      
    def forget(self, irc, msg, args):
      if len(args) == 1:
        usernick = args[0]
      elif len(args) == 0:
        usernick = msg.nick
      else:
        irc.reply("Usage: @forget [nick (optional]")
        return
      
      result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri WHERE {?uri foaf:nick ?nick .}', initBindings={'?nick': usernick} )
      
      if len(result) == 0:
        irc.reply("I don't know "+nick, prefixNick=True)
        return
        
      FOAF = self.FOAF
      userURI = list(result)[0][0]
      self.unknow(usernick, userURI)
      
      self.g.serialize('/var/www/rc98.net/zoia.rdf')
      
      irc.reply("I've forgotten who "+usernick+" is", prefixNick=True)
      
      
    def unknow(nick, userURI):
      try:
        FOAF = self.FOAF
        self.g.remove(userURI, FOAF['nick'], rdflib.Literal(usernick))
        self.g.remove(userURI, rdflib.RDF.type, FOAF['person'])
        self.g.remove(self.uri, FOAF['knows'], userURI)
      except:
        irc.reply('Error')
        raise
      
      
    def reloadfoaf(self, irc, msg, args):
      g = Graph()
      g.parse('http://michael.is.outoffoc.us/michael/zoia.rdf')
      g.serialize('/var/www/rc98.net/zoia.rdf')
      irc.reply('File copied')
      

Class = FOAF

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
