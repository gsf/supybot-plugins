###
# Copyright (c) 2005, James Vega
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

import time
import Queue
import anydbm
import random
import threading

import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.schedule as schedule
import supybot.callbacks as callbacks


class DbmMarkovDB(object):
    def __init__(self, filename):
        self.dbs = ircutils.IrcDict()
        self.filename = filename

    def close(self):
        for db in self.dbs.values():
            db.close()

    def _getDb(self, channel):
        if channel not in self.dbs:
            filename = plugins.makeChannelFilename(self.filename, channel)
            # To keep the code simpler for addPair, I decided not to make
            # self.dbs[channel]['firsts'] and ['lasts'].  Instead, we'll pad
            # the words list being sent to addPair such that ['\n \n'] will be
            # ['firsts'] and ['\n'] will be ['lasts'].  This also means isFirst
            # and isLast aren't necessary, but they'll be left alone in case
            # one of the other Db formats uses them or someone decides that I
            # was wrong and changes my code.
            self.dbs[channel] = anydbm.open(filename, 'c')
        return self.dbs[channel]

    def _flush(self, db):
        if hasattr(db, 'sync'):
            db.sync()
        if hasattr(db, 'flush'):
            db.flush()

    def addPair(self, channel, first, second, follower,
                isFirst=False, isLast=False):
        db = self._getDb(channel)
        combined = self._combine(first, second)
        if db.has_key(combined): # EW!
            db[combined] = ' '.join([db[combined], follower])
        else:
            db[combined] = follower
        if follower == '\n':
            if db.has_key('\n'):
                db['\n'] = ' '.join([db['\n'], second])
            else:
                db['\n'] = second
        self._flush(db)

    def getFirstPair(self, channel):
        db = self._getDb(channel)
        firsts = db['\n \n'].split()
        if firsts:
            return ('\n', utils.iter.choice(firsts))
        else:
            raise KeyError, 'No firsts for %s.' % channel

    def _combine(self, first, second):
        return '%s %s' % (first, second)

    def getFollower(self, channel, first, second):
        db = self._getDb(channel)
        followers = db[self._combine(first, second)]
        follower = utils.iter.choice(followers.split(' '))
        return (follower, follower == '\n')

    def firsts(self, channel):
        db = self._getDb(channel)
        if db.has_key('\n \n'):
            return len(set(db['\n \n'].split()))
        else:
            return 0

    def lasts(self, channel):
        db = self._getDb(channel)
        if db.has_key('\n'):
            return len(set(db['\n'].split()))
        else:
            return 0

    def pairs(self, channel):
        db = self._getDb(channel)
        pairs = [k for k in db.keys() if '\n' not in k]
        return len(pairs)

    def follows(self, channel):
        db = self._getDb(channel)
        # anydbm sucks in that we're not guaranteed to have .iteritems()
        # *cough*gdbm*cough*, so this has to be done the stupid way
        follows = [len(db[k].split()) for k in db.keys() if '\n' not in k]
        return sum(follows)

MarkovDB = plugins.DB('Markov', {'anydbm': DbmMarkovDB})

class MarkovWorkQueue(threading.Thread):
    def __init__(self, *args, **kwargs):
        name = 'Thread #%s (MarkovWorkQueue)' % world.threadsSpawned
        world.threadsSpawned += 1
        threading.Thread.__init__(self, name=name)
        self.db = MarkovDB(*args, **kwargs)
        self.q = Queue.Queue()
        self.killed = False
        self.setDaemon(True)
        self.start()

    def die(self):
        self.killed = True
        self.q.put(None)

    def enqueue(self, f):
        self.q.put(f)

    def run(self):
        while not self.killed:
            f = self.q.get()
            if f is not None:
                f(self.db)
        self.db.close()

class Markov(callbacks.Plugin):
    def __init__(self, irc):
        self.q = MarkovWorkQueue()
        self.__parent = super(Markov, self)
        self.__parent.__init__(irc)
        self.lastSpoke = time.time()

    def die(self):
        self.q.die()
        self.__parent.die()

    def tokenize(self, m):
        if ircmsgs.isAction(m):
            return ircmsgs.unAction(m).split()
        elif ircmsgs.isCtcp(m):
            return []
        else:
            return m.args[1].split()

    def doPrivmsg(self, irc, msg):
        if irc.isChannel(msg.args[0]):
            channel = plugins.getChannel(msg.args[0])
            canSpeak = False
            now = time.time()
            throttle = self.registryValue('randomSpeaking.throttleTime',
                                          channel)
            prob = self.registryValue('randomSpeaking.probability', channel)
            delay = self.registryValue('randomSpeaking.maxDelay', channel)
            irc = callbacks.SimpleProxy(irc, msg)
            if now > self.lastSpoke + throttle:
                canSpeak = True
            if canSpeak and random.random() < prob:
                f = self._markov(channel, irc, prefixNick=False, to=channel,
                                 Random=True)
                schedule.addEvent(lambda: self.q.enqueue(f), now + delay)
                self.lastSpoke = now + delay
            words = self.tokenize(msg)
            words.insert(0, '\n')
            words.insert(0, '\n')
            words.append('\n')
            # This shouldn't happen often (CTCP messages being the possible exception)
            if not words or len(words) == 3:
                return
            if self.registryValue('ignoreBotCommands', channel) and \
                    callbacks.addressed(irc.nick, msg):
                return
            def doPrivmsg(db):
                for (first, second, follower) in utils.seq.window(words, 3):
                    db.addPair(channel, first, second, follower)
            self.q.enqueue(doPrivmsg)

    def _markov(self, channel, irc, word1=None, word2=None, **kwargs):
        def f(db):
            minLength = self.registryValue('minChainLength', channel)
            maxTries = self.registryValue('maxAttempts', channel)
            Random = kwargs.pop('Random', None)
            while maxTries > 0:
                maxTries -= 1;
                if word1 and word2:
                    givenPair = True
                    words = [word1, word2]
                elif word1 or word2:
                    givenPair = False
                    words = ['\n', word1 or word2]
                else:
                    givenPair = False
                    try:
                        # words is of the form ['\n', word]
                        words = list(db.getFirstPair(channel))
                    except KeyError:
                        irc.error(
                            format('I don\'t have any first pairs for %s.',
                                   channel))
                        return # We can't use raise here because the exception
                               # isn't caught and therefore isn't sent to the
                               # server
                follower = words[-1]
                last = False
                resp = []
                while not last:
                    resp.append(follower)
                    try:
                        (follower,last) = db.getFollower(channel, words[-2],
                                                         words[-1])
                    except KeyError:
                        irc.error('I found a broken link in the Markov chain. '
                                  ' Maybe I received two bad links to start '
                                  'the chain.')
                        return # ditto here re: Raise
                    words.append(follower)
                if givenPair:
                    if len(words[:-1]) >= minLength:
                        irc.reply(' '.join(words[:-1]), **kwargs)
                        return
                    else:
                        continue
                else:
                    if len(resp) >= minLength:
                        irc.reply(' '.join(resp), **kwargs)
                        return
                    else:
                        continue
            if not Random:
                irc.error(
                    format('I was unable to generate a Markov chain at least '
                           '%n long.', (minLength, 'word')))
            else:
                self.log.debug('Not randomSpeaking.  Unable to generate a '
                               'Markov chain at least %n long.',
                               (minLength, 'word'))
        return f

    def markov(self, irc, msg, args, channel, word1, word2):
        """[<channel>] [word1 [word2]]

        Returns a randomly-generated Markov Chain generated sentence from the
        data kept on <channel> (which is only necessary if not sent in the
        channel itself).  If word1 and word2 are specified, they will be used
        to start the Markov chain.
        """
        f = self._markov(channel, irc, word1, word2,
                         prefixNick=False, Random=False)
        self.q.enqueue(f)
    markov = wrap(markov, ['channeldb', optional('something'),
                           additional('something')])

    def firsts(self, irc, msg, args, channel):
        """[<channel>]

        Returns the number of Markov's first links in the database for
        <channel>.
        """
        def firsts(db):
            s = 'There are %s firsts in my Markov database for %s.'
            irc.reply(s % (db.firsts(channel), channel))
        self.q.enqueue(firsts)
    firsts = wrap(firsts, ['channeldb'])

    def lasts(self, irc, msg, args, channel):
        """[<channel>]

        Returns the number of Markov's last links in the database for
        <channel>.
        """
        def lasts(db):
            irc.reply(
                format('There are %i lasts in my Markov database for %s.',
                       db.lasts(channel), channel))
        self.q.enqueue(lasts)
    lasts = wrap(lasts, ['channeldb'])

    def pairs(self, irc, msg, args, channel):
        """[<channel>]

        Returns the number of Markov's chain links in the database for
        <channel>.
        """
        def pairs(db):
            irc.reply(
                format('There are %i pairs in my Markov database for %s.',
                       db.pairs(channel), channel))
        self.q.enqueue(pairs)
    pairs = wrap(pairs, ['channeldb'])

    def follows(self, irc, msg, args, channel):
        """[<channel>]

        Returns the number of Markov's third links in the database for
        <channel>.
        """
        def follows(db):
            irc.reply(
                format('There are %i follows in my Markov database for %s.',
                       db.follows(channel), channel))
        self.q.enqueue(follows)
    follows = wrap(follows, ['channeldb'])

    def stats(self, irc, msg, args, channel):
        """[<channel>]

        Returns all stats (firsts, lasts, pairs, follows) for <channel>'s
        Markov database.
        """
        def stats(db):
            irc.reply(
                format('Firsts: %i; Lasts: %i; Pairs: %i; Follows: %i',
                       db.firsts(channel), db.lasts(channel),
                       db.pairs(channel), db.follows(channel)))
        self.q.enqueue(stats)
    stats = wrap(stats, ['channeldb'])


Class = Markov


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
