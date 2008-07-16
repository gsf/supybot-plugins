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
    conf.registerPlugin('IsItDown', True)
    if advanced:
        output('The IsItDown plugin tells you if a given URL is accessible by the rest of the world')

IsItDown = conf.registerPlugin('IsItDown')
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
