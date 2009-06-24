"""
Get a random firework from the 
Official List of Approved Fireworks for the City of Albuquerue and the County of Bernalillo
http://www.bernco.gov/upload/images/fire_rescue/fw_list_2005.pdf
"""

import re

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from random import choice
from os.path import join, dirname, abspath
import simplejson

class Fireworks(callbacks.Plugin):

    def fireworks(self, irc, msg, args):
        """
        Get a random firework from the 
        Official List of Approved Fireworks for the City of Albuquerue and the County of Bernalillo
        """
        f = join(dirname(abspath(__file__)), 'fireworks.js')
        jsonfile = open(f, 'r')
        json = simplejson.load(jsonfile)
        jsonfile.close()
        irc.reply(choice(json), prefixNick=True)

Class = Fireworks

# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
