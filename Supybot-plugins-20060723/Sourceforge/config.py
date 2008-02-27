###
# Copyright (c) 2003-2005, James Vega
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

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import output, expect, anything, something, yn
    conf.registerPlugin('Sourceforge', True)
    output("""The Sourceforge plugin has the functionality to watch for URLs
              that match a specific pattern (we call this a snarfer). When
              supybot sees such a URL, he will parse the web page for
              information and reply with the results.""")
    if yn('Do you want this snarfer to be enabled by default?'):
        conf.supybot.plugins.Sourceforge.trackerSnarfer.setValue(True)

    output("""The bugs and rfes commands of the Sourceforge plugin can be set
              to query a default project when no project is specified.  If this
              project is not set, calling either of those commands will display
              the associated help.  With the default project set, calling
              bugs/rfes with no arguments will find the most recent bugs/rfes
              for the default project.""")
    if yn('Do you want to specify a default project?'):
        project = anything('Project name:')
        if project:
            conf.supybot.plugins.Sourceforge.defaultProject.set(project)

    output("""Sourceforge is quite the word to type, and it may get annoying
              typing it all the time because Supybot makes you use the plugin
              name to disambiguate calls to ambiguous commands (i.e., the bug
              command is in this plugin and the Bugzilla plugin; if both are
              loaded, you\'ll have you type "sourceforge bug ..." to get this
              bug command).  You may save some time by making an alias for
              "sourceforge".  We like to make it "sf".""")


Sourceforge = conf.registerPlugin('Sourceforge')
conf.registerChannelValue(Sourceforge, 'trackerSnarfer',
    registry.Boolean(False, """Determines whether the bot will reply to SF.net
    Tracker URLs in the channel with a nice summary of the tracker item."""))
conf.registerChannelValue(Sourceforge, 'defaultProject',
    registry.String('', """Sets the default project to use in the case that no
    explicit project is given."""))
conf.registerGlobalValue(Sourceforge, 'bold',
    registry.Boolean(True, """Determines whether the results are bolded."""))
conf.registerGlobalValue(Sourceforge,
    'enableSpecificTrackerCommands', registry.Boolean(True, """Determines
    whether the bug, rfe, and patch commands (convenience wrappers around
    the tracker command) will be enabled."""))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
