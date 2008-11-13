
from supybot.commands import *
import supybot.callbacks as callbacks

from lxml import etree
from urllib import urlencode
import re
from urllib2 import Request, build_opener, HTTPError

SERVICE_URL = 'http://textalyser.net/?%s'
UA = 'Zoia/1.0 (Supybot/0.83; WordCount Plugin; http://code4lib.org/irc)'

def summary_stat(tree, s):
    try:
        expr ='//td[contains(text(),"%s")]' % s
        return tree.xpath(expr)[0].getnext().text
    except:
        return '?'

class WordCount(callbacks.Plugin):
    """
    Word count and text analysis of a web document,
    courtesy of http://textalyser.net
    """
    threaded = True

    def wc(self, irc, msg, args, url):
        """
        Usage: wc [url] - 
        Word count and text analysis of a web document,
        courtesy of http://textalyser.net -
        LD = Lexical Density -
        GFI = Gunning-Fog Index
        """
        postdata = urlencode(dict(count_numbers=1, is_log=1, min_char=4, site_to_analyze=url, stoplist_lang=1, words_toanalyse=10))
        opener = build_opener()
        opener.addheaders = [('User-Agent', UA)]
        req = Request(SERVICE_URL, postdata)
        try:
            doc = opener.open(req)
        except:
            irc.reply("Request to textalyser.net failed: " + sys.exc_info()[0])
            return
        parser = etree.HTMLParser()
        tree = etree.parse(doc, parser)

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
                counts[cells[i]] = int(cells[i+1])

        sortedcounts = sorted(counts.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        resp = "Top words are " + ', '.join(["%s: %d" % (k, v) for k,v in sortedcounts])

        resp += " -- Total words: %d; Different words: %d; LD: %s; GFI: %s" \
            % (int(total), int(diffwords), ld, gfi)

        irc.reply(resp)
        
    wc = wrap(wc, ['text'])

Class = WordCount

