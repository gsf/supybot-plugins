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

import xml.dom.minidom

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class FreshmeatException(Exception):
    pass

class Freshmeat(callbacks.Plugin):
    """Add the help for "@plugin help Freshmeat" here
    This should describe *how* to use this plugin."""
    threaded = True
    def callCommand(self, command, irc, msg, *args, **kwargs):
        try:
            super(Freshmeat, self).callCommand(command,irc,msg,*args,**kwargs)
        except utils.web.Error, e:
            irc.error(str(e))

    def freshmeat(self, irc, msg, args, project):
        """<project name>

        Returns Freshmeat data about a given project.
        """
        project = ''.join(project.split())
        url = 'http://www.freshmeat.net/projects-xml/%s' % project
        try:
            text = utils.web.getUrl(url)
            if text.startswith('Error'):
                text = text.split(None, 1)[1]
                raise FreshmeatException, text
            dom = xml.dom.minidom.parseString(text)
            def getNode(name):
                node = dom.getElementsByTagName(name)[0]
                return str(node.childNodes[0].data)
            project = getNode('projectname_full')
            version = getNode('latest_release_version')
            vitality = getNode('vitality_percent')
            popularity = getNode('popularity_percent')
            lastupdated = getNode('date_updated')
            irc.reply('%s, last updated %s, with a vitality percent of %s '
                      'and a popularity of %s, is in version %s.' %
                      (project, lastupdated, vitality, popularity, version))
        except FreshmeatException, e:
            irc.error(str(e))
    freshmeat = wrap(freshmeat, ['text'])


Class = Freshmeat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
