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

import time
from twisted.internet import reactor
from twisted.web import server, resource

from gwbase import BasePlugin

class WebUser(object):
    def __init__(self, user):
        self.user = user
        self.hostmask = user.gwhm
        self.rbuf = []

    def sendReply(self, reply, inreply):
        news = """
            <div>
            <span class="inreply">
            [%s]
            </span>
            <span class="reply">
            %s
            </span>
            </div>"""
        self.rbuf.append(news % (inreply.strip(), reply.strip()))

    def close(self):
        self.user.clearAuth()
        self.cb._connections.remove(self)

class WebGW(BasePlugin):
    PROTOCOL = 'http'
    USERCLASS = WebUser
    DEFAULT_PORT = 9080
    CONFIG_EXTRA = [('refreshRate', 'Integer', 15,
                        """Web interface will refresh every X seconds."""),
                    ('sessionTimeout', 'Integer', 300,
                        """Timeout for inactivity."""),
                    ('@html',None, None, """HTML Options"""),
                    ('html.replyFontSize', 'String', 'Small',
                        """Default font size for replies."""),
                    ('html.replyFontColor', 'String', 'Black',
                        """Default font color for replies."""),
                    ('html.inReplyFontColor', 'String', 'Blue',
                        """Default font color for the command calling a 
                        reply."""),
                    ('html.contentBackgroundColor', 'String', 'white',
                        """Default background color for the main content 
                        area."""),
                    ('html.generalFontSize', 'String', 'small',
                        """Default general font size."""),
                    ('html.borderColor', 'String', '#999999',
                        """Border color for content areas."""),
                    ('html.buttonBackgroundColor', 'String', '#ededed',
                        """Default background color for input buttons.""")]
                     
    class FactoryClass(server.Site):
        def __init__(self):
            server.Site.__init__(self, MainPage())

        def makeSession(self):
            """Generate a new Session instance, and store it for future reference.
            """
            uid = self._mkuid()
            s = SBSession(self, uid)
            s.expiryTimeout = self.cb.personalRegistryValue('sessionTimeout')
            session = self.sessions[uid] = s
            reactor.callLater(s.expiryTimeout, s.checkExpired)
   
            return session

	
class SBSession(server.Session):
    def checkExpired(self):
        # If I haven't been touched in 15 minutes:
        if time.time() - self.lastModified > self.expiryTimeout:
            if self.site.sessions.has_key(self.uid):
                self.expire()
            else:
                pass
                #log.msg("no session to expire: %s" % self.uid)
        else:
            #log.msg("session given the will to live for 30 more minutes")
            reactor.callLater(self.expiryTimeout, self.checkExpired)

class MainPage(resource.Resource):

    def isAuthd(self, request):
        return hasattr(request.getSession(), 'authd')

    def getHostmask(self, request):
        return request.getSession().authd.hostmask
        
    def getRbuf(self, request):
        if len(request.getSession().authd.rbuf) > 10:
            request.getSession().authd.rbuf = request.getSession().authd.rbuf[-10:]
        return ''.join(request.getSession().authd.rbuf)
        
    def render_GET(self, request):
        refreshTime = False
        if len(request.args):
            if 'refresh' in request.args:
                refreshTime = int(request.args['refresh'].pop())
                if refreshTime < 10:
                    refreshTime = 10
        return self.render_ALL(request, self.isAuthd(request), refreshTime)

    def render_POST(self, request):
        isAuthd = self.isAuthd(request)
        if isAuthd:
            cmd = request.args['command'].pop()
            if len(cmd):
                if cmd == 'logout':
                    request.redirect('/logout')
                    return 'logging out'
		else:
                    request.getSession().site.cb.cb.receivedCommand(cmd,
                    request.getSession().authd)
        return self.render_ALL(request, isAuthd)
                    
    def render_ALL(self, request, isAuthd, refresh=10):
        rs = ''
        if refresh:
            rs = """<META HTTP-EQUIV="Refresh"
                        CONTENT="%s;
                        URL=/?refresh=%s">""" % (refresh, refresh)

        content = ''
        loginLine = ''
        if isAuthd:
            loginLine = 'You are logged in as %s.' % self.getHostmask(request)
            content = self.getRbuf(request)
        else:
            loginLine = 'You are not Logged in.'
            content = TLOGIN
        htmlopt = lambda v: \
            request.getSession().site.cb.personalRegistryValue('html.%s' % v)
        page = TALL % {'content':content,
                    'postForm': TPOST,
                    'controlBar': TCONTROL,
                    'loginLine': loginLine,
                    'fontSize':htmlopt('generalFontSize'),
                    'replySize': htmlopt('replyFontSize'),
                    'replyColor': htmlopt('replyFontColor'),
                    'inReplyColor': htmlopt('inReplyFontColor'),
                    'contentBackground': htmlopt('contentBackgroundColor'),
                    'controlBackground': htmlopt('buttonBackgroundColor'),
                    'borderColor': htmlopt('borderColor')}

        return page
    
    def getChild(self, name, request):
        if name == 'login':
            return LoginPage()
        elif name == 'logout':
            return LogoutPage()
        else:
            return self

class LogoutPage(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        if hasattr(request.getSession(), 'authd'):
            #authd = request.getSession().authd
            #authd.close()
            #del request.getSession().authd
            request.getSession().expire()
        request.redirect('/')
        return 'logout'

                
class LoginPage(resource.Resource):
    isLeaf = True
    
    def render_GET(self, request):
        request.redirect('/')
        return 'no GET'

    def render_POST(self, request):
        #request.isSecure()
        #request.getClientIP()
        un = request.args['name'].pop()
        pw = request.args['pass'].pop()
	sess = request.getSession()
        a = sess.site.cb.cb.getUser(username=un, password=pw,
                                    protocol=request.getSession().site.cb.PROTOCOL,
                                    peer=request.getClientIP())
        if a:
            sess.authd = request.getSession().site.cb.USERCLASS(a)
            sess.authd.cb = sess.site.cb
            sess.notifyOnExpire(sess.authd.close)
            sess.site.cb.authorised(sess.authd)
            request.redirect('/')
            return 'authd'
        else:
            sess.expire()
            request.redirect('/')
            return 'failed'


THEAD = """
<head>
<style>
body {
    font-size: %(fontSize)s;
    text-align: center;
    }
    
input {
    font:1em "Lucida Grande", Verdana, sans-serif;
    border: 1px %(borderColor)s solid;
    background: %(controlBackground)s;
    margin: 1px;
    padding:0;
}

#header {
    }

#main {
width: 580px;
margin:0px auto;

}
.content {
    border: %(borderColor)s solid 0.01em;
    background-color: %(contentBackground)s;
    text-align: left;
    padding:1.0em;
    margin-bottom: 1em;
    }

.bar {
    width: 580px;
    margin:0px;
    margin-bottom: 1em;
    }


.controlbar {
    color: #666666;
    background-color: %(controlBackground)s;
    border: 1px %(borderColor)s solid;
    padding:0;
    margin: 1px;
    padding: 0.5em;
    text-decoration: none;
    font-size: 0.8em;
    }

.controlcontainer {
    margin:0em;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
    text-align: right;
    }
#footer {
    }

.reply {font-size: %(replySize)s; color: %(replyColor)s; padding: 4px}
.inreply {font-size: %(replySize)s; color: %(inReplyColor)s}
.label {font-size: small; font-weigth: bold; text-align: right}
</style>
</head>
"""

TCONTROL = """
    <div class="controlcontainer">
    <a class="controlbar" href="/">refresh</a>
    <a class="controlbar" href="/logout">log out</a>
    </div>
"""

TPOST = """
    <form method="POST" class="controlcontainer">
    <div>
    <input name="command" style="{width:100%}" />
    </div>
    <div>
    <input type="submit" class="controlbar" value="Send Command" />
    </div>
    </form>
"""

TBODY = """
<body>
    <div id="main">
    <div id="header">
    <h3>Supybot Gateway Plugin Web Interface</h3>
    </div>
    <div class="bar">
        %(controlBar)s
    </div>
    <div class="content">
        %(loginLine)s
        %(content)s
    </div>
    <div class="bar">
            %(postForm)s
    </div>
    <div id="footer">
    </div>
    </div>
</body>
</html>
"""
TALL = """
%(head)s
%(body)s
""" % {'head':THEAD, 'body':TBODY}

TLOGIN = """
<div class="label">
Log in here.
</div>
<form method="POST" action="/login">
<div class="label">Username
<input name="name" />
</div>
<div class="label">Password
<input name="pass" type="password" />
</div>
<div class = "label">
<input class="controlbar" type="submit" value="Log in" />
</div>
</form>
"""

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
