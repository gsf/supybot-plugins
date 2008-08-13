
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.utils.web as web
import supybot.callbacks as callbacks

import re, logging, time
from random import randint
from BeautifulSoup import BeautifulStoneSoup as BSS

logger = logging.getLogger('supybot')
HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Sing Plugin; http://code4lib.org/irc)')

ARTIST_REST_URL = 'http://lyricwiki.org/api.php?func=getArtist&fmt=xml&artist=%s'
SONG_REST_URL = 'http://lyricwiki.org/api.php?func=getSong&fmt=xml&artist=%s&song=%s'

def tinyurl(url):
    url = 'http://tinyurl.com/api-create.php?url=%s' % web.urlquote(url)
    logger.info('fetching: ' + url)
    soup = getsoup(url)
    return str(soup)

def getsoup(url):
    xml = web.getUrl(url, headers=HEADERS)
    return BSS(xml, convertEntities=BSS.XML_ENTITIES)

def getsong(artist, title):
    try:
        url = SONG_REST_URL % (web.urlquote(artist), web.urlquote(title))
        logger.info('fetching ' + url)
        soup = getsoup(url)
        song = {}
        for k in 'artist','song','lyrics','url':
            song[k] = soup.find(k).string
        return song
    except Exception, e:
        logger.info('Exception fetching lyrics for %s by %s: %s' % (title, artist, e.message))
    return

def randtitle(artist):
    try:
        url = ARTIST_REST_URL % web.urlquote(artist)
        logger.info('fetching ' + url)
        soup = getsoup(url)
        songs = soup.findAll('item')
        if len(songs):
            song = songs[randint(0, len(songs) - 1)]
            return song.string
    except Exception, e:
        logger.info('Exception looking for songs by %s: %s' % (artist, e.message))
    return

def formatlyrics(song, startline=None):
    lines = re.split(r'[\n\r]+', song['lyrics'])
    if startline == '*':
        startline = 0
        endline = len(lines)
    else:
        if not startline or not startline.isdigit():
            matchstring = startline if startline else song['song']
            try:
                matcher = re.compile(matchstring, re.I | re.M)
                endline = [matcher.search(x) and True for x in lines].index(True) + 1
                startline = endline - 4
                logger.info('%d,%d' % (startline, endline))
                while startline < 0:
                    startline += 1; endline += 1
                    logger.info('now %d,%d' % (startline, endline))
            except:
                startline = randint(0, len(lines))
                endline = startline + 4
        else:
            startline = int(startline)
            endline = startline + 4
        while endline > len(lines):
            endline -= 1; startline -= 1

    lines = lines[startline:endline]
    return ' / '.join([l for l in lines if re.search('\S', l)])

class Sing(callbacks.Plugin):
    """
    Usage: sing artist [: title] [: * | line | pattern] 
    """
    threaded = True

    def sotd(self, irc, msg, args):
        """
        Fetches song of the day from http://lyricwiki.org
        """
        try:
            from SOAPpy import SOAPProxy
            server = SOAPProxy('http://lyricwiki.org/server.php')
            song = server.getSOTD()
            title = song['song']
            artist = song['artist']
            lyrics = self.formatlyrics(song, '*')
            irc.reply('%s by %s...' % (title, artist), prefixNick=False)
            time.sleep(2)
            irc.reply(lyrics, prefixNick=False)
            return
        except Exception, e:
            irc.reply('SOTD lookup failed: ' + e.message)
            return

    def sing(self, irc, msg, args, input):
        """
        Usage: sing artist [: title] [: * | line | pattern] --
        Example: @sing bon jovi : wanted dead or alive --
        Fetches lyrics from LyricWiki.org
        """
        args = map(lambda x: x.strip(), re.split(':', input))
        line = None
        
        try: 
            artist, title, line = args
            logger.info('got %s, %s, %s' % (artist, title, line))
        except ValueError:
            try:
                artist, title = args
                logger.info('got %s, %s' % (artist, title))
                if title == '*':
                    title = randtitle(artist)
            except:
                artist = args[0]
                logger.info('got %s' % (artist))
                title = randtitle(artist)
            if not title:
                irc.reply('No songs found by ' + artist)
                return

        song = getsong(artist, title)

        if not song or song['lyrics'] == 'Not found':
            create = 'http://lyricwiki.org/index.php?title=%s:%s&action=edit' % (artist, title)
            irc.reply('No lyrics for %s by %s. Create them? %s' % (title, artist, tinyurl(create)), prefixNick=True)
        else:
            lyrics = formatlyrics(song, line)
            irc.reply(lyrics, prefixNick=False)

    sing = wrap(sing, ['text'])

Class = Sing


