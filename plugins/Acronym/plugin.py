###
# Copyright (c) 2008, Michael B. Klein
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import harvesters

class Acronym(callbacks.Plugin):
	def __init__(self,irc):
		reload(harvesters)
		super(callbacks.Plugin,self).__init__(irc)
		
	def _harvester(self):
		return harvesters.__dict__[self.registryValue('harvesterClass')]()
	
	def acronym(self, irc, msg, args):
		"""<term> [<max_results (default: 3)>]

		Look up term(s) in an acronym dictionary.
		"""

		canned_responses = utils.gen.InsensitivePreservingDict({'FHQWHGADS':"Come on, fhqwhgads. I see you jockin' me. Tryin' to make like U NO ME." })
		
		if len(args) < 1:
			irc.reply("usage: acronym %s [<max_results (default: 3)>]" % self._harvester().usage(), prefixNick=True)
		else:	
			count = 3
			if args[-1].isdigit():
				count = int(args.pop())
			terms = (" ".join(args))

			# We could do a full entity encode, but really we just need to 
			# encode spaces and ampersands
			search_string = terms.replace(' ','+').replace('&','&amp;')
			if search_string in canned_responses:
				irc.reply(canned_responses[search_string],prefixNick=True)
			else:
				results = self._harvester().lookup(terms)
				total = len(results)
				responses = results[:count]
				showing = len(responses)
				if showing == 0:
					irc.reply("No definitions found for '%s'." % terms, prefixNick=True)
				else:
					if showing <> total:
						prefix = "Top %d of %d definitions" % (showing,total)
					elif showing > 1:
						prefix = "%d definitions" % (showing)
					else:
						prefix = "1 definition"
					irc.reply("%s for '%s': %s" % (prefix, terms," ; ".join(responses)), prefixNick=True)
		

Class = Acronym


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
