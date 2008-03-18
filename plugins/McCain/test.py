from supybot.test import *

class McCainTestCase(PluginTestCase):
    plugins = ('McCain',)
    def testMcCain(self):
        self.assertNotError('mccain')


