from supybot.test import *

class FOAFTestCase(PluginTestCase):
    plugins = ('FOAF',)
    def testFOAF(self):
        self.assertNotError('knows')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
