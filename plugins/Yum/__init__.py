###

"""
Provides a calorie count and a recipe search command
"""

import supybot
import supybot.world as world

__version__ = "0.1"

__author__ = supybot.authors.unknown

__contributors__ = {}

__url__ = '' # 'http://supybot.com/Members/yourname/Yum/download'

import config
import plugin
reload(plugin) # In case we're being reloaded.
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    import test

Class = plugin.Class
configure = config.configure

