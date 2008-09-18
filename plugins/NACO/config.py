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
    conf.registerPlugin('NACO', True)
    if advanced:
        output('The NACO plugin normalizes text for comparison purposes according to the rules of http://www.loc.gov/catdir/pcc/naco/normrule.html')

IsItDown = conf.registerPlugin('NACO')
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
