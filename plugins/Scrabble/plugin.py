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

class Scrabble(callbacks.Plugin):
    """Calculates the Scrabble value of a word.
    """
    pass

    def calculate(self,word):
      letters = 'abcdefghijklmnopqrstuvwxyz'
      values = [1,3,3,2,1,4,2,4,1,8,5,1,3,1,1,3,10,1,1,1,1,4,4,8,4,10]
      
      total_value = 0
      current_value = 0
      usable_letters = 0
      for char in word.lower():
        index = letters.find(char)
        if index == -1:
          if '23'.find(char) > -1:
            current_value *= (int(char) - 1)
          else:
            current_value = 0
        else:
          usable_letters += 1
          current_value = values[index]
        total_value += current_value
      if usable_letters > 7:
        total_value += 50
      return(total_value)
    
    def checkmodifier(m):
      return((1 < m) and (m < 4))
      
    def scrabble(self, irc, msg, args, word, modifier):
      """<word> [<word_score_modifier = 2|3>]
      Use 2 after a letter for double-letter score, 3 for triple-letter score. Includes 50-point bonus for words > 7 letters.
      """
      result = self.calculate(word)
      if modifier != None:
        result *= modifier
      irc.reply(str(result),prefixNick=True)

    scrabble = wrap(scrabble,['somethingWithoutSpaces',optional(('int',"2|3",checkmodifier))])
    
Class = Scrabble


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
