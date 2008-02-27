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

import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

try:
    import twisted.web.server as server
    import twisted.web.resource as resource
    import twisted.python.htmlizer as htmlizer
    import twisted.internet.reactor as reactor
except ImportError:
    # in case twisted is not installed
    reactor = None

class Webserver(callbacks.Plugin):
    """Add the help for "@plugin help Webserver" here
    This should describe *how* to use this plugin."""
    pass

    def __init__(self, irc):
        callbacks.Plugin.__init__(self, irc)
        if not reactor:
            self.irc.error('Twisted is not installed.')
        self.irc = irc
        self.site = server.Site(Home(self))
        self.children = {}
        self.listener = None
        self._startListening()

    def flush(self):
        callbacks.Plugin.flush(self)
        self._stopListening()
        self._startListening()
        
    def _startListening(self, port=None):
        """Start the server listening."""
        if not port:
            port = self.registryValue('port')
        self.listener = reactor.listenTCP(port, self.site)

    def _stopListening(self):
        """Stop the server listening."""
        if self.listener:
            self.listener.stopListening()

    def addSite(self, name, resource):
        self.children[name] = resource

    def removeSite(self, name):
        if name in self.children:
            del self.children[name]

    def die(self):
        self._stopListening()


class SBPage(resource.Resource):
    isLeaf = True
    def __init__(self, cb):
        self.cbPlugin = cb
        resource.Resource.__init__(self)

    def renderAll(self, request, opts={}):
        opts['title'] = self.renderTitle(request)
        opts['content'] = self.renderContent(request)
        opts['heading'] = self.renderHeader(request)
        opts['tbar-fg'] = 'white'
        opts['tbar-bg'] = '#000099'
        opts['homeaddr'] = self.cbPlugin.registryValue('homeURL')
        return HTML_PAGE % opts

    def renderContent(self, request):
        return 'empty page'

    def renderHeader(self, request):
        return '%s' % self.__class__

    def renderTitle(self, request):
        return "My Supybot's Home Page"

    def renderNavbar(self, request):
        return 'no nav bar'

    def renderRecent(self, request):
        return 'recent'

    def render_GET(self, request):
        return self.renderAll(request)

    def render_POST(self, request):
        return self.renderAll(request)
  
class Home(SBPage):

    isLeaf = False

    def renderContent(self, request):
        chlist = ['<div>Hello, I am a '
                    '<a href="http://supybot.com">Supybot</a>. '
                    'I am currectly on the following IRC networks:</div>']
        for irc in world.ircs:
            chlist.append('<br /><div class="minihead">'
                            '<a href="/%s">%s</a> (%s)'
                            'as %s</div>'% (irc.network,
                                irc.network, irc.server, irc.nick))
            for name, channel in irc.state.channels.iteritems():
                chlist.append('<div class="success">'
                                '<a href="/%s/%s/">%s</a></div>' % \
                (irc.network, name[1:], name))
        return ''.join(chlist)
    
    def renderHeader(self, request):
        return 'Home Page'

    def renderTitle(self, request):
        return 'My Supybot'
    
    def getChild(self, path, request):
        child = None
        for irc in world.ircs:
            if irc.network == path:
                child = irc
                break
        if child:
            return NetworkPage(irc, self.cbPlugin)
        else:
            return self

class NetworkPage(SBPage):
   
    isLeaf = False
   
    def __init__(self, irc, cb):
        SBPage.__init__(self, cb)
        self.irc = irc

    def getChild(self, path, request):
        cname = '#%s' % path
        if cname in self.irc.state.channels:
            return ChannelPage(cname, self.irc,
            self.cbPlugin)
        else:
            return self
   
    def renderHeader(self, request):
        return 'Network Page for %s' % self.irc.network
  
    def renderTitle(self, request):
        return 'My Supybot/%s' % self.irc.network
  
    def renderContent(self, request):
        T= """
        <div><span>Name: </span><span>%s</span></div>
        <div><span>Server: </span><span>%s</span></div>
        <div><span>Nickname: </span><span>%s</span></div>
        <div><span>Channels: </span><span>(%s)</span></div>
        <div>
        %s
        </div>
        """

        C= """
        <div><a href="/%s/%s">%s</a></div>
        """
        L = []
        for c in self.irc.state.channels:
            L.append(C % (self.irc.network, c[1:], c))
        
        return T % (self.irc.network,
                    self.irc.server,
                    self.irc.nick,
                    len(L),
                    ''.join(L))
        
           
class ChannelPage(SBPage):
   
    isLeaf = False
   
    def __init__(self, cname, irc, cb):
        SBPage.__init__(self, cb)
        self.irc = irc
        self.name = cname
       
    def getChild(self, path, request):
        if path in self.cbPlugin.children:
            return self.cbPlugin.children[path](self.irc, self.name, self.cbPlugin)
        else:
            return self
        
       
    def refreshState(self):
        self.channel = self.irc.state.channels[self.name]
       
    def renderContent(self, request):
        T= """
        <div><span>Name: </span><span>%s</span></div>
        <div><span>server: </span><span>%s</span></div>
        <div><span>Ops: </span><span>(%s)</span></div>
        <div><span>Voiced: </span><span>(%s)</span></div>
        <div><span>Users: </span><span>(%s)</span></div>
        <div><span>Topic: </span><span>%s</span></div>
        <div>
        <h4>Available Sites</h4>
        %s
        </div>
        """
        self.refreshState()
        return T % (self.name,
                    self.irc.server,
                    len(self.channel.ops),
                    len(self.channel.voices),
                    len(self.channel.users) - len(self.channel.ops) - len(self.channel.voices),
                    self.channel.topic,
                    self.renderSites())
        
    def renderSites(self):
        L = []
        for k in self.cbPlugin.children:
            L.append('<div><a href="/%s/%s/%s">%s</a></div>' % \
                        (self.irc.network, self.name[1:], k, k))
        return ''.join(L)

class PluginPage(SBPage):
    
    def __init__(self, irc, channel, cb):
        SBPage.__init__(self, cb)
        self.irc = irc
        self.cname = channel
        self.cbPlugin = cb

    def renderURL(self):
        return "/%s/%s" % (self.irc.network, self.cname[1:])

class SBError(SBPage):

    def __init__(self, code, cb):
        SBPage.__init__(self, cb)
        self.code = code
        
    def renderContent(self, request):
        return '%s %s' % self.code
        
    #def getChild(self):
    #    pass

Class = Webserver


HTML_PAGE = """

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<title>%(title)s</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<style type="text/css" media="all">

body {
    font-size: 0.7em;
    margin-left: 10px;
    margin-right: 10px;
    background-color: white;
    padding: 10px;
    }

h1 {
    padding-top: 0.5em;
    font-size: 1.4em;
    }

a {
    text-decoration:none;
    }

input {
    font-family: "Lucida Grande", Verdana, Lucida, Helvetica, Arial, sans-serif;
    visibility: visible;
    border: 1px solid #8cacbb;  
    color: Black;
    background-color: white;
    vertical-align: middle;
}

textarea {
    border: 1px solid #8cacbb;  
    background-color: white;
}

code {
    font-size: 0.9em;
}

#titlecontainer {
    color: %(tbar-fg)s;
    text-align: right;
    background-color: %(tbar-bg)s;
    margin-top: 20px;
    padding-right: 0.2em;
    }

#title {
    font-size: 1.4em;
}

#recent {
    float: right;
    margin-left: 10px;
    padding-left: 10px;
    height: 400px;
    padding-right: 10px;
    border: 1px solid #8cacbb;
    height: 100%%;
}

#bodycontainer {
    position: relative;
    padding: 5px;
}

#navcontainer {
    position absolute;
    left: 0px;
    text-align: left;
    font-weight: bold;
}

#content {
    left: 150px;
    text-align: left;
}

a.nav {
    color: white;
    font-size: 0.7;
    padding: 2px;
}

div.error {
    color: #990000;
    font-weight: bold;
    }

div.success {
    color: #009900;
    font-weight: bold;
    }

div.minihead {
    font-size 1.2em;
    font-weight: bold;
    padding: 1em;
    }

span.linenumber {
    font-size: 0.8em;
    color: #999999;
    padding: 0.2em;
    }

span.line {
    font-family: Monospace, Courier, System, Fixed
}

</style>

</head>
<body>
    
<div id="titlecontainer">
    <div id="title">
        %(title)s
    </div>
    <div id="navcontainer">
        <a href="/" class="nav">
            back home  
        </a>
    </div>
</div>
<h3>
    %(heading)s
</h3>
<div id="bodycontainer">
      <div id="content">
        %(content)s
    </div>
   </div>

</body>
</html>
"""
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=78:
