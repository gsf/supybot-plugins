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
import supybot.world as world
import supybot.dbi as dbi
import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.log as log

import os
import cgi
import time
import datetime
import cStringIO as StringIO

try:
    PageModule = world.ircs[0].getCallback('Webserver').classModule
    PageClass = PageModule.plugin.PluginPage
except Exception, e:
    log.error('Webserver plugin must be loaded')

class Pastebin(callbacks.Plugin):
    """A pastebin including web server."""
    def __init__(self, irc):
        callbacks.Plugin.__init__(self, irc)
        self.db = PastebinDB()
        self.mostrecent = []
        self.serverPlugin = irc.getCallback('Webserver')
        if not self.serverPlugin:
            irc.error('Webserver plugin must be running')
        else:
            PastebinHome.cbPastebin = self
            self.serverPlugin.addSite('PasteBin', PastebinHome)
 
    def doPaste(self, irc, cname, nick, text, ip):
        date = time.time()
        pid = self.db.addPaste(poster=nick, post=text, ip=ip, date=date)
        self.mostrecent.append(pid)
        if len(self.mostrecent) > self.registryValue('recentPasteCount'):
            self.mostrecent.pop(0)
        if self.registryValue('announce'):
            url = '%s/%s/%s/PasteBin?view=%s' % \
                (conf.supybot.plugins.Webserver.rootURL().rstrip('/'),
                    irc.network, cname[1:], pid)
            mess = 'Pastebin: New paste by %s at %s' % \
                (nick, format('%u', url))
            m = ircmsgs.notice(cname, mess)
            irc.sendMsg(m)
        return pid
   
    def mostRecent(self):
        for pid in self.mostrecent:
            yield self.db.get(pid)
        
   
    def die(self):
        self.serverPlugin.removeSite('paste')

class PastebinDB(object):
    def __init__(self):
        basedir = conf.supybot.directories.data.dirize('Pastebin')
        if not os.path.exists(basedir):
            os.mkdir(basedir)
        dbpath = os.path.join(basedir, 'pastes.db')
        self.db = dbi.DB(dbpath, Record=PastebinRecord, Mapping='cdb')

    def getPaste(self, pid):
        return self.db.get(pid)

    def addPaste(self, **kw):
        newPaste = PastebinRecord(**kw)
        pid = self.db.add(newPaste)
        return pid            
        
class PastebinHome(PageClass):
    isLeaf = True
    def renderContent(self, request):
        self.cbPlugin.log.critical('%s %s', dir(request), request.method)
        segments = []
        pastetext = ''
        prenick = ''
        if request.method == 'GET':
            if 'view' in request.args and len(request.args):
                pid = request.args['view'].pop()
                try:
                    goodid = int(pid)
                except ValueError:
                    goodid = None
                if goodid:
                    record = self.cbPastebin.db.getPaste(goodid)
                    segments.append(self.renderView(request, record))
                    pastetext = record.post
                else:
                    segments.append(self.renderHome(request))
            else:
                segments.append(self.renderHome(request))
        else:
            #post (we know this since no other requests ever get here)
            segments.append(self.renderPost(request))
        segments.append(self.renderForm(prenick, pastetext))
        return ''.join(segments)

    def renderView(self, request, record):
        date =  time.asctime(time.localtime(record.date))
        lines = []
        for i, line in enumerate(record.post.splitlines()):
            lines.append(XHTML_LINE % (i,
                cgi.escape(line).replace(' ', '&nbsp;')))
        return XHTML_VIEW % (record.poster, date, ''.join(lines))

    def renderHome(self, request):
        T = """
            <h4>Make a paste</h4>
            <div>this paste will be announced in
            <a href="%s">%s</a></div>
            """
        return T % (self.renderURL, self.cname)
           
    def renderRecent(self):
        t = """
        <div>
        %s
        </div>
        """
        L = []
        for r in self.cbPastebin.mostRecent():
            L.append(r)
       
    def renderPost(self, request):
        out = {}
        if  'text' in request.args and len(request.args['text'][0]):
            text = request.args['text'].pop()
            nick = 'Anonymous'
            if 'nick' in request.args and len(request.args['nick'][0]):
                nick = request.args['nick'].pop()
            host = request.host.host
            pid = self.cbPastebin.doPaste(self.irc, self.cname, nick, text, host)
            out['success'] = 'success'
            out['message'] = ('Successful Paste<br>'
                                '<a href="%s/PasteBin?view=%s">'
                                'Go to your post'
                                '</a>') % (self.renderURL(), pid)
        else:
            out['success'] = 'Failure'
            out['message'] = 'You entered bad details.'
        return HTML_PDONE % out
    
    def renderForm(self, prenick, pastetext):
        form = {}
        form['url'] = self.renderURL()
        form['prenick'] = prenick
        form['pastetext'] = pastetext
        return HTML_PFORM % form

HTML_PFORM = """
<br /><br />
<form action="%(url)s/PasteBin" method="post">
<div>
Name:
<input type="text" size="24" maxlength="24" name="nick"
value="%(prenick)s" />
<input type="checkbox" name="savename" />Save my name
<br />
<textarea name="text" cols="80" rows="20" wrap="off">%(pastetext)s</textarea><br />
<input type="submit" value="Make Paste"/>
</form>
</div>
"""

HTML_PDONE = """
<div class="%(success)s">
%(message)s
</div>
"""

       

class PastebinRecord(dbi.Record):
    __fields__ = ['poster',
                  'ip',
                  'date',
                  'post']
 
def beautifyTimeDelta(delta):
    L = []
    if delta.days:
        L.append('%s days')
    else:
        seconds = delta.seconds
        hours, seconds = divmod(seconds, 3600)
        seconds, minutes = divmod(seconds, 60)
        if hours:
            L.append('%s hours' % hours)
        elif minutes:
            L.append('%s minutes' % minutes)
        else:
            L.append('%s seconds' % seconds)
    return ','.join(L)

                   
Class = Pastebin

#The html templates
#could move them, but why bother?

XHTML_LINE = """
<div>
<span class="linenumber">%s</span>
<span class="line">%s</span>
</div>
"""

XHTML_VIEW = """
<div class="pasteheader">Posted by %s at %s</div>
<br />
<div>
%s
</div>
"""
XHTML_BADVIEW = """The selected paste was not found."""

XHTML_RECENT = """
<div class="recentitem">
<a href="/view?pid=%s">%s</a>
<div>
%s
</div>
</div>
"""

XHTML_PASTED = """
<div class="success">You have successfully pasted.</div>
<a href="/view?pid=%s">Go to your paste</a>
"""

XHTML_BADFORM = """
<div class="error">You failed to enter the correct for details.</div>
"""

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=78:
