from supybot.commands import *
import supybot.callbacks as callbacks
import re

from elementtidy import TidyHTMLTreeBuilder
from urllib2 import urlopen

class CrazyHot(callbacks.Privmsg):

    def apa(self,irc,msg,args):
        irc.reply(self.fetch('APA',args[0]))

    def mla(self,irc,msg,args):
        irc.reply(self.fetch('MLA',args[0]))

    def ama(self,irc,msg,args):
        irc.reply(self.fetch('AMA',args[0]))

    def chicago(self,irc,msg,args):
        irc.reply(self.fetch('Chicago',args[0]))

    def fetch(self,type,isbn):
        from socket import setdefaulttimeout
        setdefaulttimeout(60)
        ns = 'http://www.w3.org/1999/xhtml'
        url = 'http://thatscrazyhot.com/search/searchisbn?citetype=%s&search=%s' % (type,isbn)
        tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        for e in tree.findall('.//{%s}div' % ns):
            if e.attrib.get('id') == 'leftcolumn':
                return self.get_text(e)
        return "isbn %s not found" % isbn

    def get_text(self,e):
        string = ''
        if e.text: string += e.text
        for child in e.getchildren():
            string += self.get_text(child)
        if e.tail: string += e.tail
        string = string.replace("\n",'')
        string = re.sub('^.*\d seconds ago','', string)
        return string

Class = CrazyHot 


