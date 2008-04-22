from supybot.test import *

class RickCheckTestCase(PluginTestCase):
    plugins = ('RickCheck',)
    def testRickCheck(self):
        self.assertResponse(
          'rickcheck http://inkdroid.org/tmp/code4lib_rules.txt', 
          'DANGER: RickRoll detected in http://inkdroid.org/tmp/code4lib_rules.txt')


