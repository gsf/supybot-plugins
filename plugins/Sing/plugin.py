
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re, logging, time
from htmlentitydefs import name2codepoint
from urllib import urlencode
from urllib2 import Request, build_opener, HTTPError
from random import randint
from SOAPpy import SOAPProxy

from BeautifulSoup import \
    BeautifulStoneSoup as BSS, \
    BeautifulSoup as BS, StopParsing

logger = logging.getLogger('supybot')

class Sing(callbacks.Plugin):
    """
    Usage: sing artist [: title] [: * | line | pattern] 
    """
    threaded = True

    def __init__(self,irc):
        self.__parent = super(Sing, self)
        self.__parent.__init__(irc)
        ua = 'Zoia/1.0 (Supybot/0.83; Sing Plugin; http://code4lib.org/irc)'
        self.server = SOAPProxy('http://lyricwiki.org/server.php')

    def sotd(self, irc, msg, args):
        """
        Fetches song of the day from lyricswiki
        """
        try:
            song = self.server.getSOTD()
            title = song['song']
            artist = song['artist']
            lyrics = self.formatlyrics(song['lyrics'])
            irc.reply('%s by %s...' % (title, artist), prefixNick=False)
            time.sleep(2)
            irc.reply(lyrics, prefixNick=False)
            return
        except Exception, e:
            logger.info(e)
            irc.reply('Error communicating with server: ' + e.message)
            return

    def sing(self, irc, msg, args, input):
        """
        Usage: sing artist [: title] [: * | line | pattern] --
        Example: @sing bon jovi : wanted dead or alive --
        Fetches lyrics from LyricWiki.org
        """
        line = None
        args = map(lambda x: x.strip(), re.split(':', input))
        
        try: 
            artist, title, line = args
            logger.info('%s, %s, %s' % (artist, title, line))
        except ValueError:
            try:
                artist, title = args
            except:
                irc.reply('random song selection not implemented')
                return

        try:
            song = self.getsong(artist, title)
        except Exception, e:
            logger.info(e)
            irc.reply('error commuincating with lyricwiki: ' + e.message)

        if song['lyrics'] == 'Not found':
            irc.reply('No lyrics found for %s : %s' % (artist, title), prefixNick=True)
        else:
            lyrics = self.formatlyrics(song, line)
            irc.reply(lyrics, prefixNick=False)

    def getsong(self, artist, title):
        return self.server.getSong(artist, title)

    def formatlyrics(self, song, startline=None):
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

    sing = wrap(sing, ['text'])

Class = Sing


