from urllib import urlencode
from urllib2 import urlopen 
from sgmllib import SGMLParser
from random import randint

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Web2(callbacks.Privmsg):

    from random import Random
    rand = Random()

    vBased = ["geotag-based","cellphone-based","tag-based", "social", "web-based" ,"rss-based", "opml-based", "greasemonkey extension for", "community" ]
    vProd = ["web services","classifieds","collaborative document editing","search engine","dating","news","widgets","instant messaging", "email", "bookmarks", "apps" ,"podcasts", "movies", "reviews", "maps","invites" ,"photos", "television", "micropayments", "auctions" ,"shopping", "textbooks" ,"wiki", "blogs"]
    vVia = ["via email invite *only*","via XML","on the desktop","via ajax", "via bittorrent", "via flash", "via shockwave" ,"via maps api","via Ruby on Rails", "via instant messaging", "via microformats", "via api mashups"]

    vPrefix = ["Squi","G","Meeb","zV","Yah","Inf","Ri","Blin","Sec","Trip","Del","Zim"]
    vMidfix = ["oo","ee","odi","eli","oli","ti","ko","onomo","ono",""]
    vPostfix = ["doo","le","rati","bo","ki","ya","gami","hub","roll","blog", "orb" ,"mojo", "ious", "ent","no","wy","share","ink","jax","tix"]
    vLibrary = ["aacr2", "mods", "mads", "ead", "tei", "sru", "z39.50", "marc",
    "openurl", "cataloging", "acquisitions", "call numbers", "dewey", "zoom",
    "purls", "isbns", "issns", "ontologies", "classifications"]
    vLibraryVerbs = ["integrating", "mixing in", "enabling", "syndicating",
    "redirecting", "revamping", "revitalizing"]
                                                                                
    quotes = [ "tagging not tanonomy",
        "user as contributor",
        "participation not publishing",
        "radical decentralization",
        "rich user experiences",
        "enabling the long tail",
        "radical trust",
        "an attitude not a technology",
        "trust your users",
        "the long tail",
        "small pieces loosely joined",
        "data as the 'Intel Inside'",
        "hackability",
        "the perpetual beta",
        "the right to remix",
        "software that gets better the more people use it",
        "emergent - user behavior not predetermined",
        "play",
        "granular addressibility of content",
        "rich user experience" ]

    def web2(self,irc,msg,args):
        """
        fetch a random quality of the Web2.0
        """
        import random
        irc.reply(Web2.quotes[ random.randint(0, len(Web2.quotes)-1) ])

    def idea(self,irc,msg,args):
        """generate web2 company name and product
        """
        company = self.pick(self.vPrefix) + \
            self.pick(self.vMidfix) + \
            self.pick(self.vPostfix)
        product = self.pick(self.vBased) + " " + \
            self.pick(self.vProd) + " " + \
            self.pick(self.vVia) 
        irc.reply("%s - %s" % (company,product))

    def library2(self,irc,msg,args):
        """generate a library2.0 idea
        """
        company = self.pick(self.vPrefix) + \
            self.pick(self.vMidfix) + \
            self.pick(self.vPostfix) + "lib"
        product = self.pick(self.vBased) + " " + \
            self.pick(self.vProd) + " " + \
            self.pick(self.vVia) + " " + \
            self.pick(self.vLibraryVerbs) + " " + \
            self.pick(self.vLibrary)
        irc.reply("%s = %s" % (company,product))

    def pick(self,array):
        return array[self.rand.randint(0,len(array)-1)]

Class = Web2 

# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
