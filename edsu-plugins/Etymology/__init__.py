"""
Consults http://www.etymonline.com/ for the meaning of words.
"""

import supybot
import supybot.world as world
import config
import plugin
reload(plugin) # In case we're being reloaded.

Class = plugin.Class
configure = config.configure
