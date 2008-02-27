"""
Determine a bogus monetary value for a blog using 
http://www.business-opportunities.biz/projects/how-much-is-your-blog-worth
"""

import supybot
import supybot.world as world
import config
import plugin
reload(plugin) # In case we're being reloaded.

Class = plugin.Class
configure = config.configure
