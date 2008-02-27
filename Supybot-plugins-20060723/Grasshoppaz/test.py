###
# Copyright (c) 2004, James Vega
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

class GrasshoppazTestCase(ChannelPluginTestCase):
    plugins = ('Grasshoppaz',)
    def testS(self):
        self.feedMsg('foo bar baz')
        self.assertResponse('s baz qux', 'foo bar qux')
        self.assertError('s blue baz')

    def testWin(self):
        self.assertRegexp('win foo', 'couldn\'t find')
        self.assertRegexp('win foo', 'only found one')
        self.assertRegexp('win foo', self.nick)

    def testSearchFlags(self):
        Grasshoppaz = conf.supybot.plugins.Grasshoppaz
        orig = Grasshoppaz.caseInsensitiveSearch()
        try:
            Grasshoppaz.caseInsensitiveSearch.setValue(True)
            self.feedMsg('foo')
            self.assertResponse('s FOO bar', 'bar')
            Grasshoppaz.caseInsensitiveSearch.setValue(False)
            self.assertRegexp('s FOO bar', 'couldn\'t find')
        finally:
            Grasshoppaz.caseInsensitiveSearch.setValue(orig)

    def testReplaceFlags(self):
        Grasshoppaz = conf.supybot.plugins.Grasshoppaz
        rorig = Grasshoppaz.globalReplace()
        sorig = Grasshoppaz.caseInsensitiveSearch()
        try:
            Grasshoppaz.caseInsensitiveSearch.setValue(True)
            Grasshoppaz.globalReplace.setValue(False)
            self.feedMsg('foo baz baz qux qux')
            self.assertResponse('s FOO bar', 'bar')
            self.assertRegexp('s baz bar', 'foo bar baz')
            Grasshoppaz.globalReplace.setValue(True)
            self.assertRegexp('s qux bar', 'baz bar bar')
        finally:
            Grasshoppaz.caseInsensitiveSearch.setValue(sorig)
            Grasshoppaz.globalReplace().setValue(rorig)

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
