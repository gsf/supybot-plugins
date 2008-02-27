###
# Copyright (c) 2004, HostPC
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
import fnmatch

import supybot.dbi as dbi
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

def now():
    return int(time.time())

class MemoRecord(dbi.Record):
    __fields__ = [
        'at',
        'by',
        'text',
        ('appends', (utils.safeEval, list)),
        ]

class DbiMemoDB(dbi.DB):
    Mapping = 'flat'
    Record = MemoRecord
    def __init__(self, *args, **kwargs):
        self.__parent = super(DbiMemoDB, self)
        self.__parent.__init__(*args, **kwargs)

    def add(self, userid, text):
        assert isinstance(userid, int)
        return self.__parent.add(self.Record(at=now(), by=userid, text=text))

    def append(self, id, userid, text):
        memo = self.get(id)
        assert isinstance(userid, int)
        memo.appends.append([now(), userid, text])
        self.set(id, memo)

MemoDB = plugins.DB('Memo', {'flat': DbiMemoDB})


class Memo(callbacks.Privmsg):
    def __init__(self, irc):
        self.__parent = super(Memo, self)
        self.__parent.__init__(irc)
        self.db = MemoDB()

    def die(self):
        self.__parent.die()
        self.db.close()

    def add(self, irc, msg, args, user, text):
        """<text>

        Adds a new memo with the text <text>.
        """
        id = self.db.add(user.id, text)
        irc.replySuccess(format('Memo #%s added.', id))
    add = wrap(add, ['user', 'text'])

    def _formatMemo(self, memo):
        user = plugins.getUserName(memo.by)
        L = [format('%s (added by %s at %t)', memo.text, user, memo.at)]
        for (at, by, text) in memo.appends:
            L.append(format('%s (appended by %s at %t)',
                            text, plugins.getUserName(by), at))
        sep = ircutils.bold(' :: ')
        return sep.join(L)

    def memo(self, irc, msg, args, id):
        """<id>

        Retrieves the memo with id <id>.
        """
        try:
            memo = self.db.get(id)
            irc.reply(self._formatMemo(memo))
        except KeyError:
            irc.errorInvalid('memo id', id)
    memo = wrap(memo, [('id', 'memo')])
        
    def search(self, irc, msg, args, glob):
        """<glob>
        
        Searches for <glob> in the memo database.
        """
        glob = glob.lower()
        def p(memo):
            if fnmatch.fnmatch(memo.text.lower(), glob):
                return True
            else:
                for (at, by, text) in memo.appends:
                    if fnmatch.fnmatch(text.lower(), glob):
                        return True
            return False
        ids = [memo.id for memo in self.db.select(p)]
        if ids:
            ids.sort()
            irc.reply(format('%L matched.', ['#%s' % id for id in ids]))
        else:
            irc.reply('There were no matching memos.')
    search = wrap(search, ['glob'])

    def append(self, irc, msg, args, user, id, text):
        """<id> <text>

        Appends <text> to the end of the memo with the given <id>.
        """
        try:
            self.db.append(id, user.id, text)
            irc.replySuccess()
        except KeyError:
            irc.errorInvalid('memo id', id)
    append = wrap(append, ['user', ('id', 'memo'), 'text'])

    def stats(self, irc, msg, args):
        """takes no arguments

        Returns the number of memos and appends in the memo database.
        """
        memos = 0
        appends = 0
        for memo in self.db:
            memos += 1
            appends += len(memo.appends)
        irc.reply(format('There are %n and %n in my memo database.',
                         (memos, 'memo'), (appends, 'append')))
    stats = wrap(stats)
              


Class = Memo

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
