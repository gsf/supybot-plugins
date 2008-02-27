"""
Talk to delicious
"""

import supybot
import supybot.world as world
import config
import plugin
reload(plugin) # In case we're being reloaded.

Class = plugin.Class
configure = config.configure
