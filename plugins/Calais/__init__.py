"""
Does stuff with Calais webservices.
"""

import supybot
import supybot.world as world

__version__ = "0.1"
__author__ = "Ed Summers"
__contributors__ = {}
__url__ = '' 

import config
import plugin
reload(plugin) # In case we're being reloaded.

if world.testing:
    import test

Class = plugin.Class
configure = config.configure
