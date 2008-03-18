from supybot.test import *

class PresidentsTestCase(PluginTestCase):
    plugins = ('Presidents',)
    def testPresidents(self):
        self.assertNotError('mccain')
        self.assertNotError('ronpaul')


