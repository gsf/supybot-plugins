from supybot.test import *

class RickCheckTestCase(PluginTestCase):
    plugins = ('RickCheck',)
    def testRickCheck(self):
        self.assertNotError('rickcheck http://inkdroid.org/tmp/code4lib_rules.txt')
        self.assertError('rickcheck')


