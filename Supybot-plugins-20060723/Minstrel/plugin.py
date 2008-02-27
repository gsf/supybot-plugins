###
# Copyright (c) 2005, Ali Afshar
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

#This is prerelease code.
#It works, that is all.
#If you want to fix something before I get around to it, please do.
import fnmatch
import time
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.utils as utils
import os
import re
import supybot.conf as conf
import supybot.dbi as dbi
import random
import supybot.log as log
import supybot.schedule as schedule

OPTIONS = {'regexp':'regexpMatcher',
            're':'regexpMatcher',
            'firstline':'glob',
            'fl':'glob',
            'title':'glob',
            't':'glob',
            'author':'glob',
            'body':'glob',
            'a':'glob',
            'choose':'',
            'c':''}

SHORTWORDS = {'re':'regexp',
                'fl':'firstline',
                't':'title',
                'a':'author',
                'c':'choose'}

PP = 2

class PoemRecord(dbi.Record):
    __fields__ = [
          'author',
          'firstline',
          'body',
          'title',
          'lastplayed',
          'totalplayings',
          'rating',
          'comments',
          'wwwid'
          ]

class Minstrel(callbacks.Plugin):
    """Minstrel plays poems. You can search its database for a poem to play,
    or you can play one from an online archive. Additionally, plain text files
    can be imported into the database. For a list of commands, please
    issue the command 'list Minstrel'.
    """
    
    def __init__(self, irc):
        callbacks.Plugin.__init__(self, irc)
        self._buildPaths()
        self._loadDb()
        self.playQueue = []

    def importfiles(self, irc, msg, args, e):
        """takes no arguments

        Import the files in the imoprt directory
        """
        self.db.importFiles()
    importfiles = wrap(importfiles, ['owner'])

    def wwwpoem(self, irc, msg, args, pid):
        """[number]


        Plays a random poem if [number] is unspecified, or the poem numbered
        [number] from the online poetry archive, at http://www.cs.rice.edu/~ssiyer/minstrels/ and stores it in the local database.
        """
        existing = self.db.wwwidExists(pid)
        if existing:
            self._debug('Poem already downloaded. Using cached poem.')
            self._play(irc, existing)
        else:
            self._debug('Downloading poem.')
            www = WwwImporter(pid=pid)
            tags = www.fetch()
            poem = self.db.add(**tags)
            if poem:
                self._debug('Successfully downloaded.')
                irc.reply('Playing from %s' % www.url)
                self._play(irc, poem)
            else:
                self._debug('Something went wrong with that one.')
                irc.reply('Sorry, the download failed.')
    wwwpoem = wrap(wwwpoem, [optional('int')])

    def poet(self, irc, msg, args, opts, globs):
        """[--regexp regexp] [--title,--t title] [--firstline,--fl firstline]
        <author> [author, ...]

        Performs a search for the <author> glob (additionally including the
        optional parameters). The author glob should be a valid glob e.g.
        Robinso* and is case-insensitive. [regexp] should be a valid regular expression,
        and will additionally search the entire content of the poem for the
        regular expression.
        """
        self._performPoemQuery(irc, opts, globs, 'author')
    poet = wrap(poet, [getopts(OPTIONS), any('glob')])

    def poem(self, irc, msg, args, opts, globs):
        """[--regexp,--re regexp] [--title,--t title] [--firstline, --fl firstline] [--
        author,--a author] <query>
        [query] ,...

        Performs a search for the <query> (additionally including the
        optional parameters). The <query> should be a valid glob e.g.
        fruit* and is case-insensitive. [regexp] should be a valid regular expression,
        and will additionally search the entire content of the poem for the
        regular expression.
        """
        self._performPoemQuery(irc, opts, globs)
    poem = wrap(poem, [getopts(OPTIONS), any('glob')])

    def _performPoemQuery(self, irc, opts, globs, *fields):
        rs = self._getPoems(opts, globs)
        if self.chooseMode:
            self._displayChoices()
        else:
            self._play(irc, self._choosePoem(rs))
       
    def _displayChoices(self):
        pass
       
    def _getPoems(self, opts, globs, *fields):
        matchers, extraopts = getOptMatchers(opts)
        self.chooseMode = 'choose' in extraopts and extraopts['choose']
        for g in globs:
            m =  (len(fields) and globMatch(g, fields)) or globMatch(g)
            matchers.append(m)
        return self.db.select(matchers)
        
    def _choosePoem(self, poems):
        highest = None
        next = True
        while next:
            try:
                poem = poems.next()
                poem.score = self._evaluatePoem(poem)
                if not highest or poem.score > highest.score:
                    highest = poem
            except StopIteration:
                next = False
        return highest

    def _evaluatePoem(self, poem):
        since = time.time() - poem.lastplayed
        score = since / (poem.totalplayings + 0.1)
        log.critical('score %s', score)
        return score

    def _play(self, irc, poem):
        if not poem:
            irc.reply('Sorry, no searches matched your thingy.')
            return
        poem.lastplayed = time.time()
        poem.totalplayings += 1
        self.db.update(poem)
        self._queueline()
        self._queueline()
        self._queueline(poem.title)
        self._queueline()
        for l in poem.body:
            self._queueline(l)
        self._queueline()
        self._queueline('(fin)')
        self._queueline(poem.author)
        if poem.wwwid:
            self._queueline(format('Downloaded from %u',
                            'http://www.cs.rice.edu/~ssiyer/minstrels'))
        self._playqueue(irc)
        #play a single poem
    
    def _queueline(self, s=' '):
        if not len(s):
            s = ' '
        self.playQueue.insert(0, s)

    def _playqueue(self, irc):
        def _playline():
            irc.reply(self.playQueue.pop(), prefixNick=False)
        start = time.time()
        for  i, v in enumerate(self.playQueue):
            schedule.addEvent(_playline, start + i * PP)
            
    def _buildPaths(self):
        self.paths = {}
        self.paths['root'] = conf.supybot.directories.data.dirize('Minstrel')
        mkdirIfNotExisting(self.paths['root'])
        self.paths['imports'] = os.path.join(self.paths['root'], 'poems')
        mkdirIfNotExisting(self.paths['imports'])

    def _loadDb(self):
        self.db = PoemDb(self.paths['root'], self.paths['imports'])

    _debug = lambda self, s: \
        self.log.debug('[Minstrel] %s' % s)

    _info = lambda self, s: \
        self.log.info('[Minstrel] %s' % s)
    
    _error = lambda self, s: \
        self.log.error('[Minstrel] %s' % s)

dataDir = conf.supybot.directories.data

def mkdirIfNotExisting(path):
     if not os.path.exists(path):
        os.mkdir(path)

class WwwImporter(object):
    #<TITLE>[minstrels] Frost at Midnight -- Samuel Taylor Coleridge</TITLE>
        
    def __init__(self, **kw):
        if 'pid' in kw and kw['pid']:
            self.pid = kw['pid']
        else:
            self.pid = random.randint(1, 1607)
        self.tags = {}
        self.url = 'http://www.cs.rice.edu/~ssiyer/minstrels/txt/%s.txt' % \
            self.pid
        log.critical(self.url)
        self.retries = 3
       
    def fetch(self):
        txt = utils.web.getUrl(self.url)
        if not 'was not found' in txt:
            L = txt.split('\n')
            L.pop()
            self.tags['title'] = L.pop(0).strip("'")
            self.tags['author'] = L.pop().split('--')[-1].strip()
            while L[0] == '': L.pop(0)
            while L[-1] == '': L.pop()
            self.tags['body'] = L
            self.tags['firstline'] = L[0]
            self.tags['wwwid'] = self.pid
            return self.tags
        else:
            log.critical('nomatch %s' % txt)
            if self.retries > 0:
                self.retries -= 1
                self.fetch()
            else:
                return None
         
class PoemDb(object):
    def __init__(self, path, importpath):
        self.root = path
        self.imports = importpath
        dbpath = os.path.join(self.root, 'poems.db')
        self.db = dbi.DB(dbpath, Record=PoemRecord)

    def add(self, **kw):
        if 'body' in kw and 'author' in kw:
            kw['firstline'] = kw['body'][0]
            if not 'title' in kw:
                kw['title'] = ''
            if not 'id' in kw:
                kw['lastplayed'] = 1
                kw['totalplayings'] = 0
                kw['rating'] = 5.0
                kw['comments'] = []
                oldPoem = self.exists(**kw)
                if oldPoem:
                    log.critical('old exists bailing')
                    return oldPoem
                else:
                    newPoem = PoemRecord(**kw)
                    self.db.add(newPoem)
                    return newPoem
        else:
            log.critical('%s' % kw)
    
    def search(self, **kw):
        return self.db.select(lambda r: True)
  
    def get(self, pid):
        return self.db.get(pid)
  
    def update(self, poem, pid=None):
        if not pid:
            pid = poem.id
        self.db.set(poem.id, poem)
  
    def exists(self, **kw):
        def match(poem):
            if poem.author == kw['author']:
                if poem.title == kw['title']:
                    if poem.firstline == kw['firstline']:
                        return True
            return False
        rs = self.select([match])
        try:
            return rs.next()
        except StopIteration:
            return None
    
    def wwwidExists(self, pid):
        def match(poem):
            print poem.wwwid
            return poem.wwwid == pid
        rs = self.select([match])
        try:
            return rs.next()
        except StopIteration:
            return None
  
    def select(self, criteria=[]):
        def match(poem):
            for p in criteria:
                if not p(poem):
                    return False
            return True
        poems = self.db.select(lambda t: match(t))
        if not poems:
            raise dbi.NoRecordError
        return poems
   
    def _importFiles(self, dirname, fnames, *args):
        for name in args[0]:
            path = os.path.join(self.imports, name)
            log.critical('II%s' , path)
            f = open(path, 'r')
            tags = {}
            for l in f:
                l = l.strip()
                if l.startswith('#'):
                    pass #comment
                elif l.startswith('@'):
                    L = l.split(' ')
                    name = L[0][1:]
                    val = ' '.join(L[1:])
                    tags[name] = val
                else:
                    tags.setdefault('body', []).append(l)
            log.critical('II%s' , tags)
            self.add(**tags)

    def importFiles(self):
        os.path.walk(self.imports, self._importFiles, None)

def getOptMatchers(opts):
    matchers = []
    extraopts = {}
    for k, v in opts:
        if k in SHORTWORDS:
            k = SHORTWORDS[k]
        if k in PoemRecord.__fields__:
            matchers.append(globMatch(v, [k]))
        elif k == 'regexp':
            matchers.append(reMatch(v))
        else:
            extraopts[k] = v
    return matchers, extraopts

def globMatch(glob, fields=['body', 'author', 'title', 'firstline']):
    globre = re.compile(fnmatch.translate(glob)[:-1], re.IGNORECASE)
    return reMatch(globre)

def reMatch(regex, fields=['body', 'author', 'title', 'firstline']):
    def match(record):
        s = ''.join([''.join(getattr(record, f)) for f in fields])
        return regex.search(s)
    return match

Class = Minstrel

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
