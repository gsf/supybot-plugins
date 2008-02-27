###
# Copyright (c) 2005, James Vega
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

import amazon

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import output, expect, anything, something, yn
    output('To use Amazon\'s Web Services, you must have a license key.')
    if yn('Do you have a license key?'):
        key = anything('What is it?')
        conf.registerPlugin('Amazon', True)
        conf.supybot.plugins.Amazon.licenseKey.set(key)
    else:
        output("""You'll need to get a key before you can use this plugin.
                  You can apply for a key at
                  http://www.amazon.com/webservices/""")


class Region(registry.OnlySomeStrings):
    validStrings = ('us', 'uk', 'de', 'jp', 'fr', 'ca')

class LicenseKey(registry.String):
    def set(self, s):
        # In case we decide we need to recover
        original = getattr(self, 'value', self._default)
        registry.String.set(self, s)
        if self.value:
            amazon.setLicense(self.value)

Amazon = conf.registerPlugin('Amazon')
conf.registerChannelValue(Amazon, 'bold',
    registry.Boolean(True, """Determines whether the results are bolded."""))
conf.registerGlobalValue(Amazon, 'licenseKey',
    LicenseKey('', """Sets the license key for using Amazon Web Services.
    Must be set before any other commands in the plugin are used.""",
    private=True))
conf.registerChannelValue(Amazon, 'linkSnarfer',
    registry.Boolean(False, """Determines whether the bot will reply to
    Amazon.com URLs in the channel with a description of the item at the
    URL."""))
conf.registerChannelValue(Amazon, 'region', Region('us',
    """Determines the region that will be used when performing searches."""))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
