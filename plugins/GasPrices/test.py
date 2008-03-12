from supybot.test import *

class GasPricesTestCase(PluginTestCase):
    plugins = ('GasPrices',)
    def testGasPrices(self):
        self.assertNotError('gasprices 22201')
        self.assertNotError('gasprices 08901 3')
        self.assertError('gasprices')

