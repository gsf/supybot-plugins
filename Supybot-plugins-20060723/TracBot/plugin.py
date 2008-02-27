###
# Copyright (c) 2005, Andrew Harvey
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

import supybot.utils as utils
from supybot.commands import *
import supybot.utils.web as web
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs

import urllib
import urllib2

class TracBot(callbacks.Plugin):
    """TracBot plugin provides plugins for use with the Trac issue tracking
    system.
    """

    def ticket(self, irc, msg, args, channel, ticketno):
        """<ticket>
        returns a link to that ticket on the Trac Site
        """
        if self.registryValue('tracBase', channel) is not "":
            base = self.registryValue('tracBase', channel) 
            reply = '%s/ticket/%d' % (base, ticketno)
        else:
            reply = "TracBot does not have a tracBase defined for this channel"
        irc.reply(reply) 
    ticket = wrap(ticket,['channel', 'int'])

    def wiki(self, irc, msg, args, channel, page):
        """<wikipage>
        returns a link to the wiki page on the Trac Site
        """
        if self.registryValue('tracBase', channel) is not "":
            base = self.registryValue('tracBase', channel)
            reply = base + '/wiki/' + page
        else:
            reply = "TracBot does not have a tracBase defined for this channel"
        irc.reply(reply)
    wiki = wrap(wiki,['channel', 'somethingWithoutSpaces'])

    def show(self, irc, msg, args, nick, page):
        """<nick> <page>
        Gives <nick> the link to <page>. Acceptable values are currently
        "bugs", "troubleshooting" and "requests"
        """
        if page == "bugs":
            reply = nick +': Learn about reporting bugs here => http://trac.adiumx.com/wiki/ReportingBugs'
        elif page == "requests":
            reply = nick + ': Learn about requesting features here => http://trac.adiumx.com/wiki/RequestingFeatures'
        elif page == "troubleshooting":
            reply = nick + ': Learn about troubleshooting AdiumX here => http://trac.adiumx.com/wiki/Troubleshooting'
        irc.reply(reply)
    show = wrap(show, ['nick', ("literal", ("bugs", "troubleshooting", "requests"), "The only currently available options are bugs, troubleshooting and requests")])

    def tracsearch(self, irc, msg, args, channel, type, page):
        """[<type>] <searchstring> 
        returns a link to a search of the Adium Trac Site for <searchstring>
        <type> can either be "wiki", "tickets", "changesets" or "commits"
        """
        if self.registryValue('tracBase', channel) is not "":
            base = self.registryValue('tracBase', channel)
            urlised = utils.web.urlquote(page)
            if type == "wiki":
                reply = base + '/search?q=' + urlised + '&wiki=on'
            elif type == "tickets":
                reply = base + '/search?q=' + urlised + '&ticket=on'
            elif type == "changesets": 
                reply = base + '/search?q=' + urlised + '&changeset=on'
            elif type == "commits":
                reply = base + '/search?q=' + urlised + '&changeset=on'
            else:
                reply = base + '/search?q=' + urlised + '&wiki=on&ticket=on&changeset=on'
        else:
            reply = "TracBot does not have a tracBase defined for this channel"
        irc.reply(reply)
    tracsearch = wrap(tracsearch,['channel', optional(('literal', ("wiki", "tickets", "changesets",  "commits"), "Borked.")), 'text'])
    
    def newticket(self, irc, msg, args, channel):
        """
        Gives the link to the trac ticket submission page.
        """
        if self.registryValue('tracBase', channel) is not "":
            base = self.registryValue('tracBase', channel)
            reply = base + '/newticket'
        else:
            reply = "TracBot does not have a tracBase defined for this channel"
        irc.reply(reply)
    newticket = wrap(newticket, ['channel'])
    
    
    def changeset(self, irc, msg, args, channel, changesetno):
        """<changeset number>
        Returns a link to changeset <changeset number> on the Adium trac site
        """
        if self.registryValue('tracBase', channel) is not "":
            base = self.registryValue('tracBase', channel)
            reply = '%s/changeset/%d' % (base, changesetno)
        else:
            reply = "TracBot does not have a tracBase defined for this channel"
        irc.reply(reply)
    changeset = wrap(changeset, ['channel', 'int'])


    def maketicket(self, irc, msg, args, channel, optlist, summary, description):
        """[--type=<type>] [--reporter=<reporter>] [--component=<component>] [--owner=<owner>] \
           [--milestone=<milestone>] [--version=<version>] "<summary>" <description> 

           Submit a new ticket with summary <summary> and description <description> with the supplied
           options.
        """
        if self.registryValue('tracBase', channel) is not "":
            base = self.registryValue('tracBase', channel)
            url = '%s/newticket' % base.rstrip('/')
            postdata={'reporter': msg.nick,
                      'summary': summary,
                      'description': description,
                      'action': 'create',
                      'status': 'new'}
            for (opt, value) in optlist:
                postdata[opt] = value
            try:
                page = self._openUrl(url, postdata)
            except:
                page = ''
            if 'id="ticket"' in page:
                number = page.split('<title>', 1)[-1].split(' ', 1)[0]
                number = number.strip('#')
                reply = ('New ticket at: %s/ticket/%s' %
                         (base.rstrip('/'), number))
            else:
                reply = 'Posting a new ticket failed.'
        else:
            reply = 'TracBot does not have a tracBase defined for this channel.'
        irc.reply(reply)
    maketicket = wrap(maketicket, ['channel',
                                   getopts({'type': None,
                                            'reporter': None,
                                            'component': None,
                                            'version': None,
                                            'milestone': None,
                                            'owner': None}),
                                   'something', 'text'])

    def _openUrl(self, url, postdata={}):
        data = urllib.urlencode(postdata)
        request = urllib2.Request(url, data=data)
        return web.getUrl(request)

    def wikipedia(self, irc, msg, args, wiki_string):
        """<wiki page>
        Returns a link to the page on wikipedia for <wiki string>
        """
        import string, urllib
        to_underscore = string.maketrans(' ', '_')
        reply = "http://en.wikipedia.org/wiki/" + urllib.quote(wiki_string.translate(to_underscore))
        irc.reply(reply)
    wikipedia = wrap(wikipedia, ['text'])

Class = TracBot

    

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
