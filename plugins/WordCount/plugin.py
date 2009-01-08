
from supybot.commands import *
import supybot.callbacks as callbacks

from StringIO import StringIO
from lxml import etree
from urllib import urlencode
import re
import sys
import socket
import supybot.utils.web as web
from urllib2 import Request, build_opener, HTTPError

SERVICE_URL = 'http://textalyser.net/?%s'
UA = 'Zoia/1.0 (Supybot/0.83; WordCount Plugin; http://code4lib.org/irc)'
httpUrlRe = re.compile(r"(https?://[^\])>\s]+)", re.I)

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

    def wc(self, irc, msg, args, url_or_text):
        """
        Usage: wc [url or text] - 
        Word count and text analysis of a web document,
        courtesy of http://textalyser.net -
        LD = Lexical Density -
        GFI = Gunning-Fog Index
        """
        params = dict(count_numbers=1, is_log=1, min_char=4, stoplist_lang=1, words_toanalyse=10)

        if web.httpUrlRe.match(url_or_text):
            params['site_to_analyze'] = url_or_text
        else:
            params['text_main'] = url_or_text

        postdata = urlencode(params)
        opener = build_opener()
        opener.addheaders = [('User-Agent', UA)]
        req = Request(SERVICE_URL, postdata)
        socket.setdefaulttimeout(20)

        try:
            doc = opener.open(req)
            html = doc.read()
        except:
            irc.reply("Request to textalyser.net failed: " + sys.exc_info()[0])
            return
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
        cells = [x.strip() for x in cells if re.match(r'\S', x)][4:]
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

