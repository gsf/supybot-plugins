from urllib import urlencode
from urllib2 import urlopen 
from xml.etree import ElementTree as ET
from elementtidy import TidyHTMLTreeBuilder
from re import match

from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class LastItem:
    """
    Class for fetching last record added information from OCLC
    and will provide it as an object with attributes like title,
    author, etc.
    """

    bib = {}
    ns = 'http://www.w3.org/1999/xhtml'
    url = "http://www.oclc.org/worldcat/grow/default.aspx"

    def __getattr__(self,name):
        if self.bib.has_key(name):
            return self.bib[name]
        else:
            raise AttributeError, name
        
    def __init__(self):
        ns = { 'ns' : LastItem.ns }
        tree = TidyHTMLTreeBuilder.parse(urlopen(self.url))
        root = tree.getroot()
        cells = root.findall('.//{%(ns)s}table/{%(ns)s}tr/{%(ns)s}td' % ns )
        self.date = cells[0].find('.//{%(ns)s}br' % ns).tail.strip()
        self.holdings = cells[2].text.replace('Total holdings in WorldCat: ','')
        self.title = cells[6].text
        self.author = cells[8].text
        self.publisher = cells[10].text
        if len(cells) == 17:
            self.contributedby = cells[16].text
        else:
            self.contributedby = cells[18].text

    def __str__(self):
        return "[%s #%s] %s %s %s uploaded by %s" % \
            (self.date, self.holdings, self.title, self.author, self.publisher,
                    self.contributedby)


class OCLC(callbacks.Privmsg):
    """
    OCLC junk
    """

    def naf(self,irc,msg,args):
        """<naf>

        Lookup a personal name in the NAF file at OCLC. Hits
        marked with a ~ are considered fuzzy matches.
        """

        try:
            from socket import setdefaulttimeout
            setdefaulttimeout(60)
            alcme = "http://alcme.oclc.org/eprintsUK/services/NACOMatch"
            name = ' '.join(args)
            query = urlencode( { \
                "method"          : "getCompleteSelectedNameAuthority",
                "serviceType"     : "rest",
                "name"            : name,
                "maxList"         : "10",
                "isPersonalName"  : "true" } )

            url = urlopen( alcme + "?" + query)
            tree = ET.parse(url)
            elem = tree.getroot()

            matches = elem.findall("match")
            if len(matches) == 0 or len(matches[0]) == 0:
                irc.reply("no match for %s" % name)
            else:
                match_count = len(matches)
                response_chunks = []
                count = 0
                for match in matches:
                  count += 1
                  established_form = match.findtext('establishedForm')
                  uri = match.findtext('uri')
                  citation = match.findtext('citation')
                  match_type = match.attrib['type']
                  match_flag = ''
                  if match_type == 'FuzzyFirstName':
                    match_flag = '~'
                  response_chunks.append("[%s%i] %s <%s>" % (match_flag, count, 
                      established_form, uri))
                irc.reply( ("[%i matches] " % count) + 
                    '; '.join(response_chunks).encode('utf8'))
        except Exception, e:
            self.log.error(str(e))
            irc.reply("dublin, there is a problem")


    def worldcat(self,irc,msg,args):
        """<worldcat>

        Last record entered into OCLC.
        """

        last = LastItem()
        irc.reply( last )

    def inst(self,irc,msg,args):
        """<institution>

        Look up a oclc participating institution by code
        """
        from elementtree.ElementTree import tostring
        from socket import setdefaulttimeout
        from re import sub
        setdefaulttimeout(60)
        ns = 'http://www.w3.org/1999/xhtml'
        inst = args[0]
        self.log.info("looking up oclc institution %s" % inst)
        url = "http://www.oclc.org/common/cgi-oclc/pi.pl?max=1&sym=%s" % inst
        response = ""
        try:
            tree = TidyHTMLTreeBuilder.parse( urlopen(url) )
            root = tree.getroot()
            info = tostring(root.findall('.//{%s}font'%ns)[8])
            response = sub("<.*?>",'', info.replace("\n",' '))
        except:
            response = "sorry no hits for %s" % inst
        irc.reply(response)

Class = OCLC 
