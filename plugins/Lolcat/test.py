from supybot.test import *

class LolcatTestCase(PluginTestCase):
    plugins = ('Lolcat',)
    def testLolcat(self):
        self.assertNotError('lolrand')
        self.assertNotError('randlol')

