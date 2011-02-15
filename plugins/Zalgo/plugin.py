###
# Copyright (c) 2010, Michael B. Klein
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

from random import randint

zalgo_up = [            
    u'\u030d', u'\u030e', u'\u0304', u'\u0305', u'\u033f', u'\u0311', u'\u0306', u'\u0310', 
    u'\u0352', u'\u0357', u'\u0351', u'\u0307', u'\u0308', u'\u030a', u'\u0342', u'\u0343', 
    u'\u0344', u'\u034a', u'\u034b', u'\u034c', u'\u0303', u'\u0302', u'\u030c', u'\u0350', 
    u'\u0300', u'\u0301', u'\u030b', u'\u030f', u'\u0312', u'\u0313', u'\u0314', u'\u033d', 
    u'\u0309', u'\u0363', u'\u0364', u'\u0365', u'\u0366', u'\u0367', u'\u0368', u'\u0369', 
    u'\u036a', u'\u036b', u'\u036c', u'\u036d', u'\u036e', u'\u036f', u'\u033e', u'\u035b', 
    u'\u0346', u'\u031a'                      
]

zalgo_down = [
    u'\u0316', u'\u0317', u'\u0318', u'\u0319', u'\u031c', u'\u031d', u'\u031e', u'\u031f', 
    u'\u0320', u'\u0324', u'\u0325', u'\u0326', u'\u0329', u'\u032a', u'\u032b', u'\u032c', 
    u'\u032d', u'\u032e', u'\u032f', u'\u0330', u'\u0331', u'\u0332', u'\u0333', u'\u0339', 
    u'\u033a', u'\u033b', u'\u033c', u'\u0345', u'\u0347', u'\u0348', u'\u0349', u'\u034d', 
    u'\u034e', u'\u0353', u'\u0354', u'\u0355', u'\u0356', u'\u0359', u'\u035a', u'\u0323'
]

zalgo_mid = [
    u'\u0315', u'\u031b', u'\u0340', u'\u0341', u'\u0358', u'\u0321', u'\u0322', u'\u0327',
    u'\u0328', u'\u0334', u'\u0335', u'\u0336', u'\u034f', u'\u035c', u'\u035d', u'\u035e',
    u'\u035f', u'\u0360', u'\u0362', u'\u0338', u'\u0337', u'\u0361', u'\u0489'           
]

class Zalgo(callbacks.Plugin):

    def rand_zalgo(self,array):
      return array[randint(0,len(array)-1)]

    def is_zalgo_char(self,c):
      return (c in (zalgo_up + zalgo_down + zalgo_mid))

    def zalgo2(self, irc, msg, args, opts, str):
      """[--up] [--down] [--size (min|normal|max)] <text>
      
      To invoke the hive-mind representing chaos. Invoking the feeling of chaos. With out order. 
      The Nezperdian hive-mind of chaos. Zalgo.	He who Waits Behind The Wall. ZALGO! http://www.eeemo.net/"""

      opt_size = 'normal'
      opt_up = False
      opt_mid = True
      opt_down = False
      
      for (opt, arg) in opts:
          if opt == 'size':
            opt_size = arg
          if opt == 'up':
            opt_up = True
          if opt == 'down':
            opt_down = True
              
      new_str = []
      for c in str:
        if self.is_zalgo_char(c):
          continue

        new_str.append(c)
        
        if opt_size == 'normal':
          num_up = randint(0,16) / 2 + 1
          num_mid = randint(0,6) / 2
          num_down = randint(0,16) / 2 + 1
        elif opt_size == 'min':
          num_up = randint(0,8)
          num_mid = randint(0,2)
          num_down = randint(0,8)
        elif opt_size == 'max':
          num_up = randint(0,64) / 4 + 3
          num_mid = randint(0,16) / 4 + 1
          num_down = randint(0,64) / 4 + 3

        if opt_up:
          for i in range(num_up):
            new_str.append(self.rand_zalgo(zalgo_up))
        if opt_mid:
          for i in range(num_mid):
            new_str.append(self.rand_zalgo(zalgo_mid))
        if opt_down:
          for i in range(num_down):
            new_str.append(self.rand_zalgo(zalgo_down))

      irc.reply(u''.join(new_str).encode('utf-8'), prefixNick=True)

    zalgo2 = wrap(zalgo2, [getopts({'up':'','down':'','size':('literal',('min','normal','max'))}), 'text'])
    
Class = Zalgo


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
