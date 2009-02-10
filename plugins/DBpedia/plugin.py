
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from lxml import etree
from StringIO import StringIO
import supybot.utils.web as web
from urllib import urlencode

import rdflib

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Sing Plugin; http://code4lib.org/irc)')
SERVICE_URL = 'http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryClass=String&MaxHits=10&%s'
NSMAP = {'ns':'http://lookup.dbpedia.org/'}

class DBpedia(callbacks.Plugin):
    """Methods for searching DBpedia"""
    threaded = True

    def uri(self, irc, msg, args, term):
        """
        find the most-likely DBpedia URIs for a given keyword(s)
        """
        results = self._search(term)
        if not len(results):
            irc.reply("no matches :(")
            return
        resp = '; '.join([ "%s - %s" % (c,u) for l,c,u in results])
        irc.reply("DBpedia has URIs for... %s" % resp)

    uri = wrap(uri, ['text'])

    def describe(self, irc, msg, args, uri):
        """print out some extracted text for a given RDF resource URI
        """
        parts = self._describe(uri)
        if len(parts) > 0:
            irc.reply('; '.join(parts).encode('utf-8'))
        else:
            irc.reply('sorry something went wrong, i am a strange hack')

    describe = wrap(describe, ['text'])

    def ducky(self, irc, msg, args, term):
        """find the first resource hit in dbpedia for a string
        """
        results = self._search(term)
        if len(results) >= 1:
            uri = results[0][2]
            parts = self._describe(uri)
            desc = '; '.join(parts)
            irc.reply('<%s> %s' % (uri, desc).encode('utf-8'))
        else:
            irc.reply('better luck next time')

    ducky = wrap(ducky, ['text'])

    def _search(self, term):
        xml = web.getUrl(SERVICE_URL % urlencode({ 'QueryString': term }), headers=HEADERS)
        parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
        tree = etree.parse(StringIO(xml), parser)
        results = []
        for r in tree.xpath('//ns:Result', namespaces=NSMAP):
            label = r.xpath('ns:Label/text()', namespaces=NSMAP)[0]
            uri = r.xpath('ns:URI/text()', namespaces=NSMAP)[0]
            category = r.xpath('ns:Categories/ns:Category/ns:Label/text()', namespaces=NSMAP)[0]
            results.append((label,category,uri))
        return results

    def _describe(self, uri):
        g = rdflib.ConjunctiveGraph()
        g.load(uri)
        parts = []
        for s, p, o in g:
            if type(o) == rdflib.Literal and o.language == 'en':
                if '#' in p:
                    label = p.split('#')[-1]
                else:
                    label = p.split('/')[-1]
                parts.append("%s: %s" % (label, o))
        return parts

Class = DBpedia


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
