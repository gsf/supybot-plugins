from supybot.test import *

class Motivate(PluginTestCase):
    plugins = ('Motivate',)
    def testMotivate(self):
        self.assertNotError('motivate')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
