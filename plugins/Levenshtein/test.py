from supybot.test import *

class LevenshteinTestCase(PluginTestCase):
    plugins = ('Levenshtein',)
    def testLevenshtein(self):
        self.assertNotError('levenshtein "cathy marshall" "paul jones"')
        self.assertHelp('levenshtein')

