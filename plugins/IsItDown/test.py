from supybot.test import *

class IsItDownTestCase(PluginTestCase):
    plugins = ('IsItDown',)
    def testIsItDown(self):
        self.assertResponse('isitdown laurentian.za?', 'Huh?')
