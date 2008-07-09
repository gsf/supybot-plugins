"""
Random band name from the house of chudnov.
http://www-personal.umich.edu/~dchud/fng/names.html
"""

import supybot
import supybot.world as world
import config
import plugin
reload(plugin) # In case we're being reloaded.

Class = plugin.Class
configure = config.configure
