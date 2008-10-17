from urllib import urlencode
from urllib2 import urlopen 
from sys import argv
from sgmllib import SGMLParser

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Parser ( SGMLParser ): 
    """
    A simple HTML parser to look for the second span of class black-18
    """

    seen = 0
    text = ""
    anagram = ""

    def start_span(self, attrs):
        attrs = dict(attrs)
        if attrs.has_key('class') and attrs['class'] == 'black-18':
            self.seen += 1

    def end_span(self):
        if self.seen == 2:
            self.anagram = self.text
            self.seen = 3

    def handle_data(self,data):
        self.text = data.strip().replace("'","").replace(".","")

class Anagram(callbacks.Privmsg):

    def ana(self,irc,msg,args):
        """ana

        generate an anagram 
        """

        phrase = ' '.join(args)
        if len(phrase) > 30:
            #irc.reply( "truncating at 30 chars" )
            phrase = phrase[0:30]

        query = urlencode( { \
            "source_text"                  : phrase, 
            "seen"                         : "true",
            "submitbutton"                 : "Generate Anagrams" } )

        url = urlopen( "http://www.anagramgenius.com/server.php?" + query )
        html = url.read()

        parser = Parser()
        parser.feed( html )

        irc.reply( parser.anagram )

    def hussein(self, irc, msg, args):
        """Hussein-ify your anagram!"""
        args.insert(1, "Hussein")
        self.ana(irc, msg, args)

Class = Anagram

# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
