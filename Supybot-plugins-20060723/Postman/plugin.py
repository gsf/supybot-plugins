###
# Copyright (c) 2005, Jeremiah Fincher
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
import popen2

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Postman(callbacks.Privmsg):
    def send(self, irc, msg, args, address, text):
        """<address> <text>

        Sends an email to <address> with contents <text>.
        """
        now = time.strftime(conf.supybot.reply.format.time(), time.localtime())
        subjectFormat = self.registryValue('subject')
        subject = ircutils.standardSubstitute(irc, msg, subjectFormat)
        mail = popen2.Popen4(['mail', '-s', subject, address])
        introFormat = self.registryValue('introduction')
        intro = ircutils.standardSubstitute(irc, msg, introFormat)
        mail.tochild.write(intro)
        mail.tochild.write('\n\n')
        mail.tochild.write(text)
        mail.tochild.close()
        status = mail.wait()
        if not status:
            irc.replySuccess(format('Email sent to %s.', address))
        else:
            errorLines = mail.fromchild.readlines()
            errorMsg = utils.str.normalizeWhitespace(' '.join(errorLines))
            irc.error(format('Mail returned %s: %s', status, errorMsg))
    send = wrap(send, ['owner', 'email', 'text'])


Class = Postman


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
