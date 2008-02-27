from os.path import dirname, abspath
from re import compile

def wogrofubico(args):
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

    print "%i" % count

