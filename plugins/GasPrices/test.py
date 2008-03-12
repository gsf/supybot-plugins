from supybot.test import *

class GasPricesTestCase(PluginTestCase):
    plugins = ('GasPrices',)
    def testGasPrices(self):
        self.assertNotError('gasprices 22201')
        self.assertError('gasprices')

