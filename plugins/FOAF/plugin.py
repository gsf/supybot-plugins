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
      
    def _uri_of_user(self, nick):
      result = self.g.query( 'PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?uri WHERE {<http://www.code4lib.org/id/zoia> foaf:knows ?uri . ?uri foaf:nick ?nick .}', initBindings={'?nick': nick} )
      if len(result) > 0:
        userURI = list(result)[0][0]
        return(userURI)
      else:
        return(None)

    def _forget_user(self, nick):
      userURI = self._uri_of_user(nick)
      if userURI != None:
        FOAF = self.FOAF
        self.g.remove((self.uri, FOAF['knows'], userURI))
        self.g.remove((userURI, FOAF['nick'], rdflib.Literal(nick)))
        self.g.remove((userURI, rdflib.RDF.type, FOAF['Person']))
        
    def _know_user(self, nick, uri):
      self._forget_user(nick)
      FOAF = self.FOAF
      userURI = rdflib.URIRef(uri)
      self.g.add((userURI, rdflib.RDF.type, FOAF['Person']))
      self.g.add((userURI, FOAF['nick'], rdflib.Literal(nick)))
      self.g.add((self.uri, FOAF['knows'], userURI))

    def _knows(self, uri1, uri2):
      userGraph = Graph()
      userGraph.parse(uri1)
      result = list(userGraph.triples((uri1,self.FOAF['knows'],uri2)))
      return len(result) > 0
      
    def _save_graph(self):
      self.g.serialize('/var/www/rc98.net/zoia.rdf')
      
    def forget(self, irc, msg, args):
      """

      Forgets the URI associated with the nick of the calling user.
      """
      self._forget_user(msg.nick)
      self._save_graph();
    forget = wrap(forget,[])
      
    def knows(self, irc, msg, args, usernick1, usernick2):
      """<nick1> <nick2>

      Determines if the two given nicks know each other based on their registered FOAFs.
      """
      userURI1 = self._uri_of_user(usernick1)
      userURI2 = self._uri_of_user(usernick2)
      knows1 = self._knows(userURI1, userURI2)
      knows2 = self._knows(userURI2, userURI1)
      
      if knows1 and knows2:
        irc.reply(usernick1 + ' and ' + usernick2 + ' know each other.', prefixNick=True)
      elif knows1:
        irc.reply(usernick1 + ' knows ' + usernick2 + ', but ' + usernick2 + ' does not know ' + usernick1 + '.', prefixNick=True)
      elif knows2:
        irc.reply(usernick1 + ' does not know ' + usernick2 + ', but ' + usernick2 + ' knows ' + usernick1 + '.', prefixNick=True)
      else:
        irc.reply(usernick1 + ' and ' + usernick2 + ' do not know each other.', prefixNick=True)
        
    knows = wrap(knows,['text','text'])

    def known(self, irc, msg, args, usernick):
      """<nick>

      Returns the URI associated with the given nick.
      """
      userURI = self._uri_of_user(usernick)
      if userURI == None:
        irc.reply("I don't know "+usernick+"'s URI")
      else:
        irc.reply(usernick+"'s URI is <"+userURI.__str__()+">", prefixNick=True)
    known = wrap(known,['text'])
        
    def know(self, irc, msg, args, uri):
      """<foaf-uri>

      Associates the given URI with the nick of the user making the call. If the nick
      already has a URI, it will be forgotten.
      """
      self._know_user(msg.nick, uri)
      self._save_graph()

      irc.reply('Your URI is now <'+uri+'>', prefixNick=True)
    know = wrap(know,['text'])
    
#    def reloadfoaf(self, irc, msg, args):
#      g = Graph()
#      g.parse('http://michael.is.outoffoc.us/michael/zoia.rdf')
#      g.serialize('/var/www/rc98.net/zoia.rdf')
#      irc.reply('File copied')
      

Class = FOAF

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
