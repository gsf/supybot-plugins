#! /usr/bin/env python

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
import os
import sys

from optparse import OptionParser
import twisted.internet.reactor as reactor
import twisted.internet.protocol as protocol

SOCKPATH = os.path.expanduser('~/.supybot-external-notice.%s')

class SupyClient(protocol.DatagramProtocol):
    """ Simple datagram sending-only protocol. """

    def sendNotice(self, botnick, network, channel, data):
        command = ' '.join([network, channel, data])
        self.transport.write(command, SOCKPATH % botnick)

def main():
    """ Parse the options, generate the data and send. """
    usage = 'usage: %prog [options] <network> <channel>'
    parser = OptionParser(usage)
    parser.add_option('-s', '--stdin', dest='stdin', action='store_true',
                  default=False, help='Read notice data from stdin.')
    parser.add_option('-f', '--formatter', dest='formatter',
                      help='formatter to apply to notice body')
    options, args = parser.parse_args()
    if len(args) < 3:
        parser.print_help()
        sys.exit(1)
    botnick = args.pop(0)
    network = args.pop(0)
    channel = args.pop(0)
    if options.stdin:
        data = sys.stdin.read()
    else:
        data = args.pop(0)
    if options.formatter:
        if options.formatter in FORMATTERS:
            data = FORMATTERS[options.formatter](data)
    client = SupyClient()
    reactor.listenUNIXDatagram(0, client)
    client.sendNotice(botnick, network, channel, data)

# An example formatter
def format_svn_commit_mail(data):
    """ Formatter for svn commits. """
    import email
    message = email.message_from_string(data)
    lines = message.get_payload().splitlines()
    author = lines.pop(0)
    date = lines.pop(0)
    revision = 'Rev: %s' % lines.pop(0).split(': ', 1)[-1]
    lines.pop(0)
    lines.pop(0)
    filename = 'File: %s' % lines.pop(0).strip()
    lines.pop(0)
    log = lines.pop(0).strip()
    return 'Svn Commit: %s, %s, %s, %s, %s' % (revision, author, date,
                                                filename, log)

def format_darcs_commit_mail(data):
    """Formatter for darcs commits"""
    import email
    message = email.message_from_string(data)
    lines = message.get_payload().splitlines()
    author = lines[0]
    log = lines[4].strip('[')
    patchnum = lines[5].split('**')[-1].strip('] {')
    headers = dict(message._headers)
    date = headers['Date']
    mlist = headers['To'].split('@')[0]
    return 'Darcs Commit: %s #%s, %s, Date: %s, Msg: %s' % (mlist, 
                                        patchnum, author, date, log)

FORMATTERS = {'svn-commit-mail':format_svn_commit_mail,
              'darcs-commit-mail':format_darcs_commit_mail}

if __name__ == '__main__':
    main()
