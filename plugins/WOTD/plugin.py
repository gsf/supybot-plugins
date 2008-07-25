
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulStoneSoup as BSS
from BeautifulSoup import BeautifulSoup as BS
from urllib2 import urlopen, Request
import re

def tinyurl(url):
    r = Request('http://tinyurl.com/api-create.php?url=%s' % url)
    doc = urlopen(r)
    soup = BSS(doc)
    return str(soup)

class WOTD(callbacks.Plugin):
    """Add the help for "@plugin help WOTD" here
    This should describe *how* to use this plugin."""
    threaded = True

    def wotd(self, irc, msg, args):
        """
        returns Merriam-Webster's Word of the Day,
        including link to mp3 audio usage example
        """
        try:
            idx = args[0]
        except:
            idx = 0
        r = Request('http://www.merriam-webster.com/word/index.xml')
        doc = urlopen(r)
        html = doc.read()
        soup = BSS(html, convertEntities=BSS.XML_ENTITIES)
        item = soup.findAll('item')[int(idx)]
        mp3url = tinyurl(item.enclosure['url'])
        itemurl = tinyurl(item.link.string)
        # description is HTML in a CDATA section
        dsoup = BS(item.description.string, convertEntities=BS.HTML_ENTITIES)
        summary = ''.join(dsoup.findAll(text=True))
        summary = re.sub('\s+', ' ', summary)
        match = re.search('\d{2}, \d+ is: (.+?) Example sentence:', summary, re.I | re.M | re.S)
        worddef = match.group(1).encode('ascii', 'ignore')
        worddef = re.sub('^\s*(?P<wotd>[^\\]+)\s*', '\g<wotd> : ', worddef)
        resp = '%s (audio:%s, link:%s)' % (worddef, mp3url, itemurl)
        irc.reply(resp, prefixNick=False)

Class = WOTD

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
