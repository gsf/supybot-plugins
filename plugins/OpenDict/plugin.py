
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re
from BeautifulSoup import BeautifulSoup, StopParsing
from urllib import urlencode
from urllib2 import Request, build_opener, HTTPError
from random import randint
from htmlentitydefs import name2codepoint

def url2soup(url, qsdata={}, postdata=None, headers={}):
    """
    Fetch a url and BeautifulSoup-ify the returned doc
    """
    ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
    headers.update({'User-Agent': ua})

    params = urlencode(qsdata)
    if params:
        if '?' in url:
            url = "%s&%s" % (url,params)
        else:
            url = "%s?%s" % (url,params)
    req = Request(url,postdata,headers)
    opener = build_opener()
    doc = opener.open(req)
    data = doc.read()
    data = data.replace("\xa0", "")
    soup = BeautifulSoup(data, convertEntities=['html','xml'])
    return soup

def htmlentitydecode(s):
    return re.sub(u'&(%s);' % u'|'.join(name2codepoint), 
        lambda m: unichr(name2codepoint[m.group(1)]), s)

randurl = 'http://www3.merriam-webster.com/opendictionary/newword_display_recent.php'
def randword(irc):
    last = randint(0, 15000)
    try:
        soup = url2soup(randurl, {'last':last})
    except HTTPError, e:
        irc.reply('http error %s for %s' % (e.code, randurl), prefixNick=True); return
    except StopParsing, e:
        irc.reply('parsing error %s for %s' % (e.code, OpenDict.searchurl), prefixNick=True); return

    entries = soup.find('div','page_content_box').findAll('dt')
    if not entries:
        irc.reply('No results')
        return

    dt = entries[0]
    resp = u''.join([x.string for x in dt.contents])

    if len(dt.contents) <= 1:
        dd = dt.nextSibling.nextSibling
        resp += u' Usage: %s' % u''.join([x.string for x in dd.contents])

    resp = htmlentitydecode(resp)
    irc.reply(resp, prefixNick=False)

searchurl = 'http://www3.merriam-webster.com/opendictionary/newword_search.php'
def searchword(irc):
    try:
        soup = url2soup(searchurl, {'word':word})
    except HTTPError, e:
        irc.reply('http error %s for %s' % (e.code, OpenDict.searchurl), prefixNick=True); return
    except StopParsing, e:
        irc.reply('parsing error %s for %s' % (e.code, OpenDict.searchurl), prefixNick=True); return

class OpenDict(callbacks.Plugin):
    """Add the help for "@plugin help OpenDict" here
    This should describe *how* to use this plugin."""
    threaded = True

    def opendict(self, irc, msg, args, word):
        """
        """
        randword(irc)
        return

#        if not word:
#            randword(irc)
#        else:
#            searchword(irc, word)
#        return

    opendict = wrap(opendict, [optional('text')])

Class = OpenDict


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
