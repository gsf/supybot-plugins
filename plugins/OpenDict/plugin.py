
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

def randword(irc):
    url = 'http://www3.merriam-webster.com/opendictionary/newword_display_recent.php'
    last = randint(0, 15000)
    try:
        soup = url2soup(url, {'last':last})
    except HTTPError, e:
        irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
    except StopParsing, e:
        irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

    entries = soup.find('div','page_content_box').findAll('dt')
    if not entries:
        irc.reply('No results')
        return

    entry = parse_entry(entries[0])
    resp = htmlentitydecode(entry)
    irc.reply(resp, prefixNick=False)

def searchword(irc,word):
    url = 'http://www3.merriam-webster.com/opendictionary/newword_search.php'
    try:
        soup = url2soup(url, {'word':word})
    except HTTPError, e:
        irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
    except StopParsing, e:
        irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

    entries = soup.find('div','page_content_box').findAll('dt')[:3]
    if not entries:
        irc.reply('No results')
        return

    resp = u''.join([parse_entry(e) for e in entries])
    resp = htmlentitydecode(resp)
    irc.reply(resp, prefixNick=False)

def parse_entry(entry):
    resp = u''.join([x.string for x in entry.contents])
    dds = entry.findNextSiblings('dd')[:2]
    for dd in dds:
        s = u''.join([x.string for x in dd.contents])
        if s.find('Submitted by') != -1:
            break
        resp += u' %s' % s
    return resp

class OpenDict(callbacks.Plugin):
    """Add the help for "@plugin help OpenDict" here
    This should describe *how* to use this plugin."""
    threaded = True

    def opendict(self, irc, msg, args, word):
        """
        """
        if not word:
            randword(irc)
        else:
            searchword(irc, word)
        return

    opendict = wrap(opendict, [optional('text')])

Class = OpenDict


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
