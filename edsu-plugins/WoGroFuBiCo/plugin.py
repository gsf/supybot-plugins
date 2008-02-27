from supybot.commands import *
import supybot.callbacks as callbacks
from urllib import urlopen
from re import compile
from os.path import dirname, abspath

class WoGroFuBiCo(callbacks.Privmsg):

    def wogrofubico(self,irc,msg,args):
      """
      see how many times a word or phrase appears in WoGroFuBiCo
      """
      if len(args) == 0:
        irc.reply("must supply a word or phrase")
        return

      pattern = compile(''.join(args).lower())
      text = file(dirname(abspath(__file__))+'/WoGroFuBiCo.txt').read().lower()

      pos = 0
      count = 0
      while pos < len(text):
        match = pattern.search(text, pos)
        if not match: break
        count += 1
        pos = match.end()

      irc.reply(count)

Class = WoGroFuBiCo
