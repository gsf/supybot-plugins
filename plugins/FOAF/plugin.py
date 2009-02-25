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
      self.g.parse('http://rc98.net/zoia.rdf')
#      self.g.parse('/var/www/rc98.net/zoia.rdf', format="xml")
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
        
    def _user_graph(self, uri):
      userGraph = Graph()
      try:
        userGraph.parse(uri)
      except Exception, e:
        u = "http://www.w3.org/2007/08/pyRdfa/extract?space-preserve=true&uri=" + uri
        userGraph.parse(u, identifier=uri)
      return userGraph

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
      userGraph = self._user_graph(uri1)
      result = list(userGraph.triples((uri1,self.FOAF['knows'],uri2)))
      return len(result) > 0
      
    def _save_graph(self):
      self.g.serialize('/var/www/rc98.net/zoia.rdf')
      
    def _list(self, entities):
      result = []
      for thing in entities:
        if type(thing) == rdflib.URIRef:
          result.append('<' + str(thing) + '>')
        else:
          result.append('"' + str(thing) + '"')
      return result
      
    def common(self, irc, msg, args, predicate, nicks):
      """<foaf-predicate> <nick>, <nick>[, <nick>...]
      
      Returns the objects that all nicks have in common related to the given predicate.
      """
      commonGraph = Graph()
      uris = []
      for nick in nicks:
        userURI = self._uri_of_user(nick)
        if userURI == None:
          irc.reply("I don't know "+nick+"'s URI.")
          return
        try:
          commonGraph.parse(userURI)
        except Exception, e:
          u = "http://www.w3.org/2007/08/pyRdfa/extract?space-preserve=true&uri=" + userURI
          commonGraph.parse(u, identifier=userURI)
        uris.append(userURI)

      query = ''
      for uri in uris:
        query = query + ('<%s> ?predicate ?obj . ' % str(uri))
      
      result = commonGraph.query('SELECT ?obj WHERE { %s }' % query, initBindings={'?predicate':self.FOAF[predicate]})
      entities = []
      for entity in result:
        entities.append(entity[0])
      if len(entities) > 0:
        reply = self._list(entities)
        irc.reply(', '.join(reply),prefixNick=True)
      else:
        irc.reply('No common <foaf:' + predicate + '>s found.',prefixNick=True)
    common = wrap(common,['somethingWithoutSpaces',many('nick')])
      
    def foaf(self, irc, msg, args, nick, predicate):
      """<nick> <foaf-predicate>
      
      Returns the objects of the given predicate in the given nick's FOAF.
      """
      userURI = self._uri_of_user(nick)
      if userURI == None:
        irc.reply("I don't know "+nick+"'s URI.")
      else:
        userGraph = self._user_graph(userURI)
        result = self._list(userGraph.objects(userURI,self.FOAF[predicate]))
        irc.reply(nick + ' <foaf:' + predicate + '>: ' + ', '.join(result),prefixNick=True)
    foaf = wrap(foaf,['nick','somethingWithoutSpaces'])
    
    def predicates(self, irc, msg, args, nick, obj):
      """<nick> <nick-or-uri>
      
      Displays the relationships that have been asserted by the given nick about the
      other nick or URI.
      """
      subject = self._uri_of_user(nick)
      if subject == None:
        irc.reply("I didn't know "+nick+"'s URI anyway.")
      else:
        userGraph = self._user_graph(subject)
        match = re.search('^<(.+)>$',obj)
        if match == None:
          objURI = self._uri_of_user(obj)
          if objURI == None:
            irc.reply("I don't know "+obj+"'s URI.")
            return
        else:
          objURI = rdflib.URIRef(match.group(1))
        result = []
        for predicate in userGraph.predicates(subject, objURI):
          result.append('<' + str(predicate) + '>')
        irc.reply('Relationships asserted by ' + nick + ' about ' + obj + ': ' + ', '.join(result), prefixNick=True)
    predicates = wrap(predicates,['nick','somethingWithoutSpaces'])
            
    def forget(self, irc, msg, args, nick):
      """<nick>

      Forgets the URI associated with the given nick.
      """
      if self._uri_of_user(nick) == None:
        irc.reply("I didn't know "+nick+"'s URI anyway.")
      elif nick == 'zoia':
        irc.reply('Funny. Not.',prefixNick=True)
      else:
        self._forget_user(nick)
        self._save_graph();
        irc.reply("OK, I've forgotten " + nick + "'s URI")
    forget = wrap(forget,['nick'])
      
    def knows(self, irc, msg, args, usernick1, usernick2):
      """<nick1> <nick2>

      Determines if the two given nicks know each other based on their registered FOAFs.
      """
      userURI1 = self._uri_of_user(usernick1)
      if userURI1 == None:
        irc.reply("I don't know "+usernick1+"'s URI")
        return
        
      userURI2 = self._uri_of_user(usernick2)
      if userURI2 == None:
        irc.reply("I don't know "+usernick2+"'s URI")
        return

      try:
        knows1 = self._knows(userURI1, userURI2)
        knows2 = self._knows(userURI2, userURI1)
      except rdflib.exceptions.ParserError, e:
        irc.reply('Error: ' + str(e))
        return

      if knows1 and knows2:
        irc.reply(usernick1 + ' and ' + usernick2 + ' know each other.', prefixNick=True)
      elif knows1:
        irc.reply(usernick1 + ' knows ' + usernick2 + ', but ' + usernick2 + ' does not know ' + usernick1 + '.', prefixNick=True)
      elif knows2:
        irc.reply(usernick1 + ' does not know ' + usernick2 + ', but ' + usernick2 + ' knows ' + usernick1 + '.', prefixNick=True)
      else:
        irc.reply(usernick1 + ' and ' + usernick2 + ' do not know each other.', prefixNick=True)
    knows = wrap(knows,['nick','nick'])

    def known(self, irc, msg, args, usernick):
      """[<nick>]

      Returns the URI associated with the given nick. Defaults to the calling user. If no nick given,
      returns a list of nicks which have an associated URI.
      """
      if usernick == None:
        result = self.g.query('PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?nick WHERE { <http://www.code4lib.org/id/zoia> foaf:knows ?uri . ?uri foaf:nick ?nick }')
        users = []
        for row in result:
          users.append(row[0])
        user_list = ', '.join(sorted(users))
        irc.reply('I know URIs for the following users: ' + user_list)
      else:
        userURI = self._uri_of_user(usernick)
        if userURI == None:
          irc.reply("I don't know "+usernick+"'s URI")
        else:
          irc.reply(usernick+"'s URI is <"+str(userURI)+">", prefixNick=True)
    known = wrap(known,[optional('nick')])
        
    def know(self, irc, msg, args, nick, uri):
      """[<nick>] <foaf-uri>

      Associates the given URI with the given nick. If the nick already has a URI, 
      it will be forgotten. Defaults to the calling user.
      """
      if nick == None:
        nick = msg.nick
      self._know_user(nick, uri)
      self._save_graph()

      irc.reply(nick + "'s URI is now <"+uri+">", prefixNick=True)
    know = wrap(know,[optional('nick'),'url'])
    
#    def reloadfoaf(self, irc, msg, args):
#      g = Graph()
#      g.parse('http://michael.is.outoffoc.us/michael/zoia.rdf')
#      g.serialize('/var/www/rc98.net/zoia.rdf')
#      irc.reply('File copied')
      

Class = FOAF

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
