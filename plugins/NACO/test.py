from supybot.test import *

class NACOTestCase(PluginTestCase):
    plugins = ('NACO',)
    def testNACO(self):
        self.assertNotError('naco')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
