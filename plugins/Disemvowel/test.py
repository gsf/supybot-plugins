from supybot.test import *

class DisemvowelTestCase(PluginTestCase):
    plugins = ('Disemvowel',)
    def testDisemvowel(self):
        self.assertNotError('disemvowel')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
