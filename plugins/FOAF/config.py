import plugin

import supybot.conf as conf
import supybot.utils as utils
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import output, expect, anything, something, yn
    conf.registerPlugin('FOAF', True)
    if advanced:
        output('Parses zoia\'s FOAF file to determine if zoia knows you, or if you know zoia')

FOAF = conf.registerPlugin('FOAF')
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
