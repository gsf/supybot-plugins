###
# Copyright (c) 2005, Jeremiah Fincher
# Copyright (c) 2006, Jon Phillips
# Copyright (c) 2006, Creative Commons
# All rights reserved.
###

import time
import rfc822
import poplib
import textwrap
from cStringIO import StringIO as sio

import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from supybot.utils.iter import all

class Mailbox(callbacks.Privmsg):
    """Add the help for "@help Mailbox" here
    This should describe *how* to use this plugin."""
    """
    Module for checking a POP3 mailbox at a specified interval and posting it
    to a specified chat channel.
    """
    threaded = True
    lastCheck = 0

    # This provides a callback to self
    def callCommand(self, method, irc, msg, *args, **kwargs):
        try:
            super(Mailbox, self).callCommand(method, irc, msg, *args, **kwargs)
        except utils.web.Error, e:
            irc.error(str(e))
    
    def _checkServer(self, irc):
        user = self.registryValue('user')
        server = self.registryValue('server')
        password = self.registryValue('password')
        if not server:
            raise callbacks.Error, 'There is no configured POP3 server.'
        if not user:
            raise callbacks.Error, 'There is no configured POP3 user.'
        if not password:
            raise callbacks.Error, 'There is no configured POP3 password.'
        return (server, user, password)

    def _connect(self, server, user, password):
        pop = poplib.POP3(server)
        pop.user(user)
        pop.pass_(password)
        return pop

    def _getPop(self, irc):
        return self._connect(*self._checkServer(irc))

    def _getMsgs(self, pop):
        n = len(pop.list()[1])
        for i in range(1, n+1):
            (_, lines, _) = pop.retr(i)
            yield (i, '\r\n'.join(lines))
        
    def _quit(self, pop, delete=True):
        if delete:
            n = len(pop.list()[1])
            for i in range(1, n+1):
                pop.dele(i)
        pop.quit()

    def __call__(self, irc, msg):
        now = time.time()
        if now - self.lastCheck > self.registryValue('period'):
            try:
                try:
                    t = world.SupyThread(target=self._checkForAnnouncements,
                                         args=(irc,))
                    t.setDaemon(True)
                    t.start()
                finally:
                    # If there's an error, we don't want to be checking every
                    # message.
                    self.lastCheck = now
            except callbacks.Error, e:
                self.log.warning('Couldn\'t check mail: %s', e)
            except Exception:
                self.log.exception('Uncaught exception checking for new mail:')

    def _checkForAnnouncements(self, irc):
        start = time.time()
        self.log.info('Checking mailbox for announcements.')
        pop = self._getPop(irc)
        i = None
        for (i, msg) in self._getMsgs(pop):
            message = rfc822.Message(sio(msg))
            frm = message.get('From')
            if not frm:
                self.log.warning('Received message without From header.')
                continue
            else:
                frm = frm.rstrip()
            subject = message.get('Subject', '').rstrip()
            content = message.fp.read()
            self.log.info('Received message with subject %q from %q.',
                          subject, frm)
            if subject == 'all':
                channels = list(irc.state.channels)
            else:
                channels = subject.split()
                if not channels or not all(irc.isChannel, channels):
                    channels = list(self.registryValue('defaultChannels'))
                    if subject:
                        content = '%s: %s' % (subject, content)
                if not channels:
                    self.log.info('Received message with improper subject '
                                  'line from %s.', frm)
                    continue
            prefix = self.registryValue('prefix')
            content = utils.str.normalizeWhitespace(content)
            self.log.info('Making announcement to %L.', channels)
            chunks = textwrap.wrap(content, 350)
            for channel in channels:
                if channel in irc.state.channels:
                    maximum = self.registryValue('limit', channel)
                    for chunk in chunks[:maximum]:
                        s = self._formatChunk(
                            self._formatPrefix(prefix + " ")+chunk)
                        irc.queueMsg(ircmsgs.privmsg(channel, s))
                prefix = ''
        self._quit(pop)
        self.log.info('Finished checking mailbox, time elapsed: %s',
                      utils.timeElapsed(time.time() - start))

    # provides formatting for the prefix option
    def _formatPrefix(self, s):
        fancyprefix = self.registryValue('fancyprefix')
        if fancyprefix:
            return ircutils.bold(s)
        else:
            return s

    # provides formatting for the email message
    def _formatChunk(self, s):
        fancystyle = self.registryValue('fancystyle')
        if fancystyle:
            return ircutils.bold(ircutils.mircColor(s, 'red'))
        else:
            return s

    def check(self, irc, msg, args):
        """takes no arguments

        Checks whether email is available at the configured mailbox.
        """
        (server, user, password) = self._checkServer(irc)
        pop = self._connect(server, user, password)
        n = len(pop.list()[1])
        irc.reply(format('I have %n waiting for me.', (n, 'message')))

    def retrieve(self, irc, msg, args):
        """takes no arguments

        Retrieves the emails from the configured mailbox and prints them to
        stdout.
        """
        (server, user, password) = self._checkServer(irc)
        pop = self._connect(server, user, password)
        for (_, msg) in self._getMsgs(pop):
            print msg
        irc.replySuccess()

    # this is what is called when one asks supybot about Mailbox
    def mailbox(self, irc, msg, args, email):
        """[<email>]

        This is where one will get information about a registered email
        account <email>.
        """
        # copied the next line from the Webopedia plugin
        # self._wpBackend(irc, msg, term) 
    mailbox = wrap(mailbox, [additional('text')])

Class = Mailbox


# vim:set shiftwidth=4 softtabstop=8 expandtab textwidth=78:
