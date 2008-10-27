import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import rdflib

class Calais(callbacks.Privmsg):

    def entities(self, irc, msg, args):
        """look for entities in a web resource using http://semanticproxy.com
        """
        url = args[0]
        found = []
        g = rdflib.ConjunctiveGraph()
        key = 'q45p9he7jbyf5xk2hvmv3ue9'
        calais = "http://service.semanticproxy.com/processurl/%s/rdf/%s" % (key, url)
        name = rdflib.URIRef('http://s.opencalais.com/1/pred/name')
        g.load(calais)
        e = 'http://s.opencalais.com/1/type/em/e/'
        for s, o in g.subject_objects(predicate=rdflib.RDF.type):
            if o.startswith('http://s.opencalais.com/1/type/em/e/'):
                o_type = o.split('/')[-1]
                for o_name in g.objects(s, name):
                    found.append('a %s %s' % (o_type.lowercase(), o_name))
        if len(found) > 0:
            irc.reply("OK I found " + ', '.join(found))
        else:
            irc.reply("urm, sorry me no find anything")

Class = Calais
