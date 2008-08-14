
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.utils.web as web
import supybot.callbacks as callbacks

import re, logging, time
from random import randint
from urllib import urlencode
from BeautifulSoup import BeautifulStoneSoup as BSS

logger = logging.getLogger('supybot')
HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Sing Plugin; http://code4lib.org/irc)')

def editurl(artist, title):
    baseurl = 'http://lyricwiki.org/index.php?action=edit&'
    params = dict(title=':'.join((artist, title)))
    return baseurl + urlencode(params)

def artisturl(artist):
    baseurl = 'http://lyricwiki.org/api.php?func=getArtist&fmt=xml&'
    params = dict(artist=artist)
    return baseurl + urlencode(params)

def songurl(artist, title):
    baseurl = 'http://lyricwiki.org/api.php?func=getSong&fmt=xml&'
    params = dict(artist=artist, song=title)
    return baseurl + urlencode(params)

def tinyurl(url):
    try:
        url = 'http://tinyurl.com/api-create.php?url=%s' % url
        logger.info('fetching: ' + url)
        tiny = web.getUrl(url, headers=HEADERS)
        return tiny
    except:
        return 'http://lyricwiki.org'

def getsoup(url):
    logger.info('fetching: ' + url)
    xml = web.getUrl(url, headers=HEADERS)
    return BSS(xml, convertEntities=BSS.XML_ENTITIES)

def getsong(artist, title):
    try:
        url = songurl(artist, title)
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
        url = artisturl(artist)
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
            lyrics = formatlyrics(song, '*')
            lyrics = lyrics.encode('ascii', 'ignore')
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
            except:
                artist = args[0]
                logger.info('got %s' % (artist))
                title = randtitle(artist)
        if title == '*':
            title = randtitle(artist)
        elif not title:
            irc.reply('No songs found by ' + artist)
            return

        song = getsong(artist, title)

        if not song or song['lyrics'] == 'Not found':
            create = tinyurl(editurl(artist, title))
            irc.reply('No lyrics for %s by %s. Create them? %s' % (title, artist, create), prefixNick=True)
        else:
            lyrics = formatlyrics(song, line)
            lyrics = lyrics.encode('ascii', 'ignore')
            irc.reply(lyrics, prefixNick=False)

    sing = wrap(sing, ['text'])

Class = Sing


