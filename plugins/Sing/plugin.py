
import supybot.utils as utils
from supybot.commands import *
import supybot.utils.web as web
import supybot.callbacks as callbacks

import re, logging
from random import randint

from lxml.html import iterlinks, fromstring

logger = logging.getLogger('supybot')
HEADERS = {'User-Agent': 'Zoia/1.0 (Sing Plugin; http://code4lib.org/irc)'}

def randtitle(artist):
    songs = songlist(artist)
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

def normalize(s):
    s = re.sub('\s+', '_', s.strip())
    s = re.sub('[^\w,]+', '', s)
    return s.lower()

class LyricsNotFound(Exception):
    pass

def lyricsmania_urls(artist, title):
    title_norm = normalize(title)
    artist_norm = normalize(artist)
    url = 'http://www.lyricsmania.com/%s_lyrics_%s.html' % \
        (title_norm, artist_norm)
    logger.info("Fetching %s" % url)
    html = web.getUrl(url, headers=HEADERS)
    if html.find('not in our archive') != -1:
        raise LyricsNotFound
    doc = fromstring(html)
    link = doc.xpath('//a[starts-with(@href, "/print")]')[0]
    return (url, 'http://www.lyricsmania.com/%s' % link.attrib['href'])
    
def lyricsmania(artist, title):
    try:
        (ref_url, print_url) = lyricsmania_urls(artist, title)
        logger.info("Fetching %s" % print_url)
        headers = HEADERS.copy()
        headers['Referer'] = ref_url
        html = web.getUrl(print_url, headers=headers)
        doc = fromstring(html)
        lyrics = doc.xpath('//div[@id="printprintx"]')[0]
        return {
            'artist': artist,
            'song': title,
            'lyrics': lyrics.text_content()
            }
    except LyricsNotFound:
        return None

class Sing(callbacks.Plugin):
    """
    Usage: sing artist [: title] [: * | line | pattern] 
    """
    threaded = True

    def sing(self, irc, msg, args, input):
        """
        Usage: sing artist [: title] [: * | line | pattern] --
        Example: @sing bon jovi : wanted dead or alive --
        Searches http://lyricsmania.com
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
                try:
                    title = randtitle(artist)
                except Exception, e:
                    logger.error(utils.exnToString(e))
                    irc.reply("Arrgh! Something went horribly wrong")
                    return
        if title == '*':
            try:
                title = randtitle(artist)
            except Exception, e:
                logger.error(utils.exnToString(e))
                irc.reply("Arrgh! Something went horribly wrong")
                return
        elif not title:
            irc.reply('No songs found by ' + artist)
            return

        try:
            song = lyricsmania(artist, title)
            if not song or song['lyrics'] == 'Not found':
                irc.reply("No lyrics found for %s by %s" % (title, artist))
            else:
                lyrics = formatlyrics(song, line)
                irc.reply(lyrics.encode('utf8', 'ignore'), prefixNick=False)
        except Exception, e:
            logger.error(utils.exnToString(e))
            irc.reply("Arrgh! Something went horribly wrong")

    sing = wrap(sing, ['text'])

    def songs(self, irc, msg, args, input):
        """<string>
        fetches song list from lyricsmania.com"""

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
            irc.reply(resp.encode('utf8', 'ignore'))

    songs = wrap(songs, ['text'])

def songlist(artist, searchstring=None):

    artist = normalize(artist)
    url = 'http://lyricsmania.com/%s_lyrics.html' % artist
    logger.info("Fetching " + url)
    html = web.getUrl(url, headers=HEADERS)
    doc = fromstring(html)
    
    titles = []
    for a in doc.xpath('//a'):
        if a.attrib.has_key('href') \
        and a.attrib['href'].endswith("_lyrics_%s.html" % artist):
            song = a.text_content()
            if searchstring:
                if not re.search(searchstring, song, re.I):
                    continue
            titles.append(song)

    return [re.sub(' lyrics$', '', x) for x in titles]

Class = Sing


