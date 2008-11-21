from supybot.test import *

class IsItDownTestCase(PluginTestCase):
    plugins = ('IsItDown',)
    def testIsItDown(self):
        self.assertNotError('isitdown')
#        self.assertResponse('isitdown laurentian.za?', 'Huh?')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
