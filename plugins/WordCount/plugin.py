
from supybot.commands import *
import supybot.callbacks as callbacks
import supybot.utils.web as web

from lxml import etree
from StringIO import StringIO
from urllib import urlencode
import re

SERVICE_URL = 'http://textalyser.net/?%s'
HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; WordCount Plugin; http://code4lib.org/irc)')

def summary_stat(tree, s):
    try:
        expr ='//td[contains(text(),"%s")]' % s
        return tree.xpath(expr)[0].getnext().text
    except:
        return '?'

class WordCount(callbacks.Plugin):
    """
    Detailed text analysis of a web document,
    courtesy of http://textalyser.net
    """
    threaded = True

    def wc(self, irc, msg, args, url):
        """
        Usage: wc [url] - 
        Detailed text analysis of a web document,
        courtesy of http://textalyser.net -
        LD = Lexical Density -
        GFI = Gunning-Fog Index
        """
        html = web.getUrl(SERVICE_URL % urlencode({'q': url}), headers=HEADERS)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)

        total = summary_stat(tree, 'Total word count')
        diffwords = summary_stat(tree, 'Number of different words')
        ld = summary_stat(tree, 'Lexical Density')
        gfi = summary_stat(tree, 'Gunning-Fog')
        readable = summary_stat(tree, 'Readability')

        freq_header = tree.xpath('//h3[contains(text(),"Frequency and top words")]')[0]
        wctable = freq_header.getnext()
        cells = wctable.xpath('.//text()')

        # filter out whitespace text nodes
        cells = [x for x in cells if re.match(r'\S', x)][4:]
        counts = {}
        for i in range(0, len(cells)):
            if i % 4 == 0:
                counts[cells[i]] = cells[i+1]
        items = counts.items()
        items.sort()
        resp = "Top words are " + ', '.join(["%s: %d" % (k, int(v)) for k,v in items])

        resp += "-- Total words: %d; Different words: %d; LD: %s; GFI: %s" \
            % (int(total), int(diffwords), ld, gfi)

        irc.reply(resp)
        
    wc = wrap(wc, ['text'])

Class = WordCount

