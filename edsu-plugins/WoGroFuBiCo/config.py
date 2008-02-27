import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('WoGroFuBiCo', True)

Eef = conf.registerPlugin('WoGroFuBiCo')
