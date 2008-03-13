###

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Yum', True)


Yum = conf.registerPlugin('Yum')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Yum, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))

