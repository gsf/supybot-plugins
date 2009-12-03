
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.utils.web as web
import supybot.callbacks as callbacks
from pprint import pformat

import re, logging, time
from random import randint
from urllib import urlencode
from BeautifulSoup import BeautifulStoneSoup as BSS, BeautifulSoup as BS
import html5lib
from html5lib import treebuilders

from lxml.html import iterlinks, fromstring

logger = logging.getLogger('supybot')
HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Sing Plugin; http://code4lib.org/irc)')

def getsoup(url):
    logger.info("fetching " + url)
    html = web.getUrl(url, headers=HEADERS)
    parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
    return parser.parse(html.decode('utf-8', 'ignore'), encoding='utf-8')

def randtitle(artist):
    songs = []
    try:
        songs = songlist(artist)
    except Exception, e:
        logger.error(utils.exnToString(e))
        irc.reply("Arrgh! Something went horribly wrong")
        return
    if len(songs):
        return songs[randint(0, len(songs) - 1)]

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
                logger.info('start,end: %d,%d' % (startline, endline))
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

def lyricsty_normalize(s):
    s = re.sub('[^A-Za-z0-9\s]+', '', s.strip())
    s = re.sub('\s+', '_', s)
    return s

def lyricsty(artist, title):
    try:
        title_norm = lyricsty_normalize(title)
        artist_norm = lyricsty_normalize(artist)
        artist_init = artist_norm[0]
        url = 'http://www.lyricsty.com/lyrics/%s/%s/%s.html' % \
            (artist_init.lower(), artist_norm.lower(), title_norm.lower())

        soup = getsoup(url)
        lyricsdiv = soup.find('div', {'class': 'song'})
        lyrics = ''.join([x.string for x in lyricsdiv.contents if x.string])
        song = {
            'artist': artist, 
            'song': title, 
            'lyrics': lyrics
            }
        return song
    except Exception, e:
        logger.info('Exception fetching lyrics from %s: %s' % (url, e.message))

class Sing(callbacks.Plugin):
    """
    Usage: sing artist [: title] [: * | line | pattern] 
    """
    threaded = True

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

        song = lyricsty(artist, title)

        if not song or song['lyrics'] == 'Not found':
            irc.reply('Lyricsty has no lyrics for %s by %s' % (title, artist))
        else:
            lyrics = formatlyrics(song, line)
            lyrics = lyrics.encode('ascii', 'ignore')
            irc.reply(lyrics, prefixNick=False)

    sing = wrap(sing, ['text'])

    def songs(self, irc, msg, args, input):
        """<string>
        fetches song list from lyricsty.com"""

        args = map(lambda x: x.strip(), re.split(':', input))

        try:
            artist, searchstring = args
        except:
            artist, searchstring = args[0], None

        songs = []
        try:
            songs = songlist(artist, searchstring)
        except Exception, e:
            logger.error(utils.exnToString(e))
            irc.reply("Arrgh! Something went horribly wrong")
            return

        if len(songs) == 0:
            irc.reply("No songs found")
        else:
            resp = '; '.join(songs)
            irc.reply(resp)

    songs = wrap(songs, ['text'])

def songlist(artist, searchstring=None):

    artist = artist.lower()
    artist_norm = lyricsty_normalize(artist)
    artist_init = artist_norm[0]
    url = 'http://lyricsty.com/lyrics/%s/%s' % (artist_init, artist_norm)
    
    href_match = re.compile('/lyrics/%s/%s' % (artist_init, artist_norm))

    doc = None
    try:
        logger.info("Fetching " + url)
        html = web.getUrl(url, headers=HEADERS)
        doc = fromstring(html)
    except Exception, e:
        logger.error(utils.exnToString(e))
        return []

    songtable = doc.cssselect('table.bandsongs')[0]
    
    songs = []
    for tup in songtable.iterlinks():
        elem = tup[0]
        try:
            href = elem.attrib['href']
            if not re.match(href_match, href):
                continue
        except:
            continue
        song = elem.text_content()
        if searchstring:
            if not re.search(searchstring, song, re.I):
                continue
        song = re.sub(' lyrics$', '', song)
        songs.append(song)
    return songs

Class = Sing


