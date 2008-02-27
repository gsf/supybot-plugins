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

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import output, expect, anything, something, yn
    output('To use the Acronym Finder, you must have obtained a license key.')
    if yn('Do you have a license key?'):
        key = something('What is it?')
        while len(key) != 36:
            output('That is not a valid Acronym Finder license key.')
            if yn('Are you sure you have a valid Acronym Finder license key?'):
                key = something('What is it?')
            else:
                key = ''
                break
        if key:
            conf.registerPlugin('AcronymFinder', True)
            conf.supybot.plugins.AcronymFinder.licenseKey.setValue(key)
    else:
        output("""You'll need to get a key before you can use this plugin.
                  You can apply for a key at http://www.acronymfinder.com/dontknowyet/""")

AcronymFinder = conf.registerPlugin('AcronymFinder')
conf.registerGlobalValue(AcronymFinder, 'licenseKey',
    registry.String('', """Sets the license key for using The Acronym Finder.
    Must be set before any other commands in the plugin are used.""",
    private=True))

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
