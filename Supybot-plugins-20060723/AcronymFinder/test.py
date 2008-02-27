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

from supybot.test import *

LICENSE_KEY = ''

class AcronymFinderTestCase(PluginTestCase):
    plugins = ('AcronymFinder',)
    if LICENSE_KEY:
        def setUp(self):
            PluginTestCase.setUp(self)
            conf.supybot.plugins.AcronymFinder.licensekey.set(LICENSE_KEY)

        if network:
            def testAcronym(self):
                self.assertRegexp('acronym ASAP', 'as soon as possible')
                self.assertRegexp('acronym CIA institute', 'of America')
                self.assertNotRegexp('acronym UNIX', 'not an acronym')
                # Used to pass requests with spaces ... make sure that stays fixed
                self.assertError('acronym W T F')
                # Make sure we can parse pages that have a single response, instead
                # of a list of acronyms
                self.assertNotError('acronym pebkac')
    else:
        def testNoKey(self):
            self.assertError('acronym CIA')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
