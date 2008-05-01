
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import logging

from BeautifulSoup import BeautifulSoup
import re
from urllib import urlencode
from urllib2 import Request, build_opener, HTTPError
from random import randint

logger = logging.getLogger('supybot')

class Sing(callbacks.Plugin):
    """Add the help for "@plugin help Sing" here
    This should describe *how* to use this plugin."""
    threaded = True

    def _url2soup(self, url, qsdata={}, postdata=None, headers={}):
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
        logger.info('fetching %s, %s' % (url,postdata))
        req = Request(url,postdata,headers)
        opener = build_opener()
        doc = opener.open(req)
        soup = BeautifulSoup(doc.read())
        return soup

    def sing(self, irc, msg, args, input):
        """
        Fetches lyrics from the lyricsfly.com api --
        Usage: sing artist [:title] [:line num]
        Example: @sing bon jovi : wanted dead or alive
        """

        line_idx = None
        try: 
            artist, title, line_idx = map(lambda x: x.strip(), re.split('[:\-]', input))
            line_idx = int(line_idx)
        except:
            try:
                artist, title = map(lambda x: x.strip(), re.split('[:\-]', input))
            except:
                artist = input
                try:
                    title = self._random_title(artist)
                except Exception, e:
                    irc.reply('Got exception %s: %s when searching for songs by %s' \
                    % (e.__class__, e, artist), prefixNick=True); 
                    return

        lyricsurl = 'http://lyricsfly.com/api/api.php?i=6b03519c191925472'
        qsdata = {'a': artist, 't': title}

        try:
            soup = self._url2soup(lyricsurl, qsdata)
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, lyricsurl), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, lyricsurl), prefixNick=True); return

        songs = soup('sg')
        if not songs:
            irc.reply('No results for "%s"' % input); return
        song = songs[randint(0, len(songs) - 1)]
        if not song('id'):
            irc.reply('No results for "%s"' % input); return
        lyrics = song.tx.string.replace('[br]','\n')

        if re.search('instrumental', lyrics, re.I):
            irc.reply("(humming %s by %s)" % (song.tt.string, song.ar.string), prefixNick=False)
            return

#        lyrics = lyrics.replace('\r',' ')
#        stanzas = lyrics.split('\n\n')

        # if song title is in the lyrics, narrow down to just those stanzas
        titlematch = re.compile(title, re.I | re.MULTILINE)
#        title_in_lyrics = titlematch.search(lyrics)
#        if title_in_lyrics:
#            stanzas = [s for s in stanzas if titlematch.search(s)]

#        stanza = stanzas[randint(0, len(stanzas) - 1)]
        lines = re.split('[\n\r]+', lyrics) #stanza.split("\n")
        lines = [l for l in lines if 'lyricsfly' not in l]
        lines = [l for l in lines if not re.search('written by', l, re.I)]
       
        if not line_idx:
            try:
                line_idx = [titlematch.search(x) and True for x in lines].index(True)
            except:
                try:
                    line_idx = randint(0,len(lines))
                except:
                    irc.reply("I got an empty song")
                    return

        if line_idx > 3:
            resp = lines[line_idx-4:line_idx]
        else:
            try:
                resp = lines[line_idx:line_idx+4]
            except:
                resp = lines[line_idx]
#        irc.reply('%s - %s' %(' / '.join(resp), title), prefixNick=False)
        irc.reply('%s' % ' / '.join(resp), prefixNick=False)

    sing = wrap(sing, ['text'])

    def _random_title(self, artist):
        searchurl = 'http://lyricsfly.com/search/search.php'
        postdata = urlencode({'sort': 1, 'options': 2, 'keywords': artist})
        soup = self._url2soup(searchurl,{},postdata)
        results = [a.string for a in soup.findAll('a', href=re.compile('^view.php'))]
        logger.info('num results: %d' % len(results))
        try:
            ret = results[randint(0, len(results) - 1)]
            return ret
        except:
            return 


Class = Sing


