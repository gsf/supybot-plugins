
import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Fireworks', True)

Fireworks = conf.registerPlugin('Fireworks')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
