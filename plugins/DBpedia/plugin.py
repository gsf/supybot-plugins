
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
        xml = web.getUrl(SERVICE_URL % urlencode({ 'QueryString': term }), headers=HEADERS)
        parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
        tree = etree.parse(StringIO(xml), parser)
        results = []
        for r in tree.xpath('//ns:Result', namespaces=NSMAP):
            label = r.xpath('ns:Label/text()', namespaces=NSMAP)[0]
            uri = r.xpath('ns:URI/text()', namespaces=NSMAP)[0]
            category = r.xpath('ns:Categories/ns:Category/ns:Label/text()', namespaces=NSMAP)[0]
            results.append((label,category,uri))
        if not len(results):
            irc.reply("no matches :(")
            return
        resp = '; '.join([ "%s - %s" % (c,u) for l,c,u in results])
        irc.reply("DBpedia has URIs for... %s" % resp)

    uri = wrap(uri, ['text'])

    def describe(self, irc, msg, args, uri):
        try:
            g = rdflib.ConjunctiveGraph.load(uri)
            desc = ""
            for s, p, o in d:
                if o == rdflib.Literal:
                    desc += str(o)
            irc.reply(desc.encode('utf-8'))
        except:
            irc.reply("argh, something wrong in the metaverse")


    describe = wrap(describe, ['text'])

Class = DBpedia


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
