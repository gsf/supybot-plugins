from supybot.test import *

class TrafficTestCase(PluginTestCase):
    plugins = ('Traffic',)
    def testTraffic(self):
        self.assertNotError('traffic Arlington, VA')
        self.assertNotError('traffic 22201')
        self.assertNotError('traffic Wilson Blvd., 22201')
        self.assertNotError('traffic 100 Hiram Sq., New Brunswick, NJ, 08901')
        self.assertError('traffic foobar, bazquux')

