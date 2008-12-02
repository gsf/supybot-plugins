import feedparser
import os
import re
import simplejson
import time
from BeautifulSoup import BeautifulSoup, StopParsing
from cgi import parse_qs
from datetime import date, datetime
from elementtidy import TidyHTMLTreeBuilder
from int2word import int2word
from random import randint
from urllib import quote, urlencode
from urllib2 import urlopen, urlparse, Request, build_opener, HTTPError
from urlparse import urlparse
import csv

from supybot.commands import *
import supybot.callbacks as callbacks


class PollNotFoundException(Exception):
    pass


class Assorted(callbacks.Privmsg):

    def devil(self,irc,msg,args):
        """fetch a random entry from the devil's dictionary at
        http://www.eod.com/devil/archive/ 
        """
        base = 'http://www.eod.com'
        ns = 'http://www.w3.org/1999/xhtml'
        tree = TidyHTMLTreeBuilder.parse(urlopen(base+'/devil/archive/'))

        def is_entry(a):
            if a.attrib.has_key('href') \
                and '/devil/archive/' in a.attrib['href']:
                return True
            return False

        anchors = filter(is_entry, tree.findall('.//{%s}a' % ns))
        anchor = anchors[randint(0, len(anchors)-1)]

        tree = TidyHTMLTreeBuilder.parse(urlopen(base+anchor.attrib['href']))
        word = tree.find('.//{%s}strong' % ns).text

        paras = tree.findall('.//{%(ns)s}blockquote/{%(ns)s}p' % {'ns': ns})
        irc.reply("%s - %s" % (word, paras[0].text.encode('utf8','ignore')))


    def underbelly(self,irc,msg,args):
        """access2005 podcast downloads today
        """
        text = urlopen("http://access2005.library.ualberta.ca/podcast-stats.txt").read().strip()
        irc.reply(text)

    def runoff(self,irc,msg,args):
        """polls code4libcon 2007 runoff votes
        """
        results = self.get_votes(122)
        irc.reply('; '.join(results).encode('utf8'))

    def tshirts(self,irc,msg,args):
        """code4libcon 2007 tshirt votes
        """
        results = self.get_votes(150)
        irc.reply('; '.join(results).encode('utf8'))
    
    def tshirters(self,irc,msg,args):
        """code4libcon 2007 tshirt voters
        """
        results = self.get_voters(150)
        irc.reply(("[%i voters] " % len(results)) + 
            '; '.join(results).encode('utf8'))

    def hosts2008(self,irc,msg,args):
        """code4libcon 2008 host site votes
        """
        results = self.get_votes(164)
        irc.reply('; '.join(results).encode('utf8', 'ignore'))
    
    def hosters(self,irc,msg,args):
        """code4libcon 2008 host site voters
        """
        results = self.get_voters(164)
        irc.reply(("[%i voters] " % len(results)) + 
            '; '.join(results).encode('utf8'))
 
    def votes2007(self,irc,msg,args):
        """polls code4libcon 2007 votes
        """
        results = self.get_votes(120)
        irc.reply('; '.join(results).encode('utf8'))

    def keynotes2010(self,irc,msg,args):
      """votes for the 2010 code4libcon keynote 
      """
      keynotes = [
        "Estelle Getty", "Sylvester Stallone", "Yngwie Malmsteen",
        "Andy Dick", "U. Rex Dumdum", "Michael J. Giarlo", "Ron Paul",
        "Bacon Salt", "Zoia", "Ima Hogg", "Mark Lemongello", "'anon'",
        "Trout Fishing in America", "Freddie Skunkcap", "Dick Assman",
        "Rooster McConaughey", "Hacker John", "Ace Waterwheels"
      ]
      n = randint(3,8)
      people = [keynotes.pop(randint(0, len(keynotes)-1)) for i in range(n)]
      votes = [randint(1,100) for a in range(0,n)]
      votes.sort(lambda a,b: cmp(b,a))
      results = zip(people,votes)
      msg = ["%s [%i]" % (result[0], result[1]) for result in results]
      irc.reply('; '.join(msg))

    def hosts2010(self,irc,msg,args):
      """
      Shows votes for the 2010 code4libcon. Courtesy of 
      http://www.floydpinkerton.net/fun/citynames.html
      """
      places = [
        "Aces of Diamonds, Florida", "Fearnot, Pennsylvania", "Normal, Illinois",
        "Assawoman, Virginia", "Fifty-Six, Arkansas", "Odd, West Virginia",
        "Bald Head, Maine", "Forks of Salmon, California", "Ogle, Kentucky",
        "Beetown, Wisconsin", "Fort Dick, California", "Okay, Oklahoma",
        "Belcher, New York", "Frankenstein, Missouri", "Panic, Pennsylvania",
        "Ben Hur, Texas", "Footville, Wisconsin", "Peculiar, Missouri",
        "Big Foot, Illinois", "Gaylordsville, Connecticut", "Plain City, Utah",
        "Big Sandy, Wyoming", "Gay Mills, Wisconsin", "Porkey, Pennsylvanania",
        "Blueballs, Pennsylvania", "Gun Barrel City, Texas", "Quiggleville, Pennsylvania",
        "Boring, Maryland", "Hell, Michigan", "Rambo Riviera, Arkansas",
        "Boring, Oregon", "Hicksville, Ohio", "River Styx, Ohio",
        "Buddha, Indiana", "Hooker, Arkansas", "Roachtown, Illinois",
        "Chestnut, Illinois", "Hooker, Oklahoma", "Romance, Arkansas",
        "Chicken, Alaska", "Hornytown, North Carolina", "Rough and Ready, California",
        "Chocalate Bayou, Texas", "Hot Coffee, Mississippi", "Sand Draw, Wyoming",
        "Chugwater, Wyoming", "Hot Water, Mississippi", "Sandwich, Illinois",
        "Climax, North Carolina", "Intercourse, Pennsylvania", "Smackover, Arkansas",
        "Climax, Pennsylvania", "It, Mississippi", "Spread Eagle, Wisconsin",
        "Climax, Saskatchewan", "Jupiter, Florida", "Toad Suck, Arkansas",
        "Cold Foot, Alaska", "Kill Devil Hills, North Carolina", "Umpire, Arkansas",
        "Cold Water, Mississippi", "King Arthur's Court, Michigan", "Uncertain, Texas",
        "Cut-Off, Louisiana", "Koopa, Colorado", "Yazoo, Mississippi",
        "Dickeyville, Wisconsin", "Lawyersville, New York", "Yeehaw Junction, Florida",
        "Ding Dong, Texas", "Lollipop, Texas", 
        "Disco, Tennessee", "Love Ladies, New Jersey", 
        "Dismal, Tennessee", "Magazine, Arkansas", 
        "Dry Fork, Wyoming", "Mars, Pennsylvania", 
        "Eclectic, Alabama", "Monkey's Elbow, Kentucky", 
        "Eek, Alaska", "Muck City, Alabama", 
        "Embarrass, Minnesota", "No Name, Colorado",
        "Gross, Nebraska",
      ]
      def rand_places(num, seen=None):
        if seen == None: 
          seen = []
        if num == 0:
          return []
        place = places[randint(0, len(places)-1)]
        if place in seen:
          place = rand_places(1, seen)
        seen.append(place)
        return [place] + rand_places(num-1, seen)
      n = randint(3,8)
      cities = rand_places(n)
      votes = [randint(1,100) for a in range(0,n)]
      votes.sort(lambda a,b: cmp(b,a))
      results = zip(cities,votes)
      msg = []
      for result in results:
        msg.append("%s [%i]" % (result[0], result[1]))
      irc.reply('; '.join(msg))

    def get_votes(self, node_id, brief=True):
        json = urlopen("http://code4lib.org/votes.php?node_id=%i" % node_id).read()
        results = []
        for tally in simplejson.loads(json):
          talk_name = tally['talk_name']
          if brief and not re.match('http', talk_name):
            talk_name = re.sub('( -|[:/.]).*', '', talk_name)
          results.append("%s %s" % (talk_name, tally['votes']))
          if brief and len(results) > 15:
            break
        return results

    def runoffers(self,irc,msg,args):
        """code4libcon 2007 runoff voters
        """
        results = self.get_voters(122)
        irc.reply(("[%i voters] " % len(results)) + 
            '; '.join(results).encode('utf8'))


    def voters2007(self,irc,msg,args):
        """code4libcon 2007 voters
        """
        results = self.get_voters(120)
        irc.reply(("[%i voters] " % len(results)) + 
            '; '.join(results).encode('utf8'))
     
    def get_voters(self, node_id):
        json = urlopen("http://code4lib.org/voters.php?node_id=%d" % node_id).read()
        results = []
        for tally in simplejson.loads(json):
          results.append("%s - %s" % (tally['name'], tally['votes']))
        return results

    def moe(self,irc,msg,args):
        """moe
        """
        ns = 'http://www.w3.org/1999/xhtml'
        url = 'http://www.snpp.com/guides/moe_calls.html'
        root = TidyHTMLTreeBuilder.parse(urlopen(url))

        bolds = root.findall('.//{%s}b' % ns)
        quote = bolds[ randint(0,len(bolds)-1) ]
        irc.reply(quote.text)

    def deli(self,irc,msg,args):
        max = 1
        url = 'http://del.icio.us/rss/popular'
        if (len(args) > 0):
            url += '/' + quote(args[0])
        if (len(args) > 1):
            max = int(args[1])

        feed = feedparser.parse(url)
        count = 0
        reply = ''
        for entry in feed.entries:
            count += 1
            if count > max: break
            reply += '%s - %s ; ' % (entry.title, entry.link)
        irc.reply(reply.encode('utf8'))

    def jihad(self,irc,msg,args):
        """welcomes a fellow jihadist

        http://www.elsewhere.org/cgi-bin/jihad
        """
        url = "http://www.elsewhere.org/cgi-bin/jihad"
        tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        strong = tree.find('.//{http://www.w3.org/1999/xhtml}strong')
        irc.reply("welcome %s!" % strong.text)

    def journal(self,irc,msg,args):
        """randomly sample a journal name
        """
        url = "http://www.code4lib.org/node/86"
        tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        list = tree.find('.//{http://www.w3.org/1999/xhtml}ul')
        names = []
        for name in list:
            names.append(name.text)
        irc.reply(names[randint(0, len(names)-1)])

    def jvotes(self,irc,msg,args):
        """journal name votes
        """
        text = urlopen("http://rsinger.library.gatech.edu/journalnamevote/overbelly_all.php").read().strip()
        irc.reply(text)

    def jvoters(self,irc,msg,args):
        """journal name voters
        """
        text = urlopen("http://rsinger.library.gatech.edu/journalnamevote/voters.php").read().strip()
        irc.reply(text)

    def lastjournal(self,irc,msg,args):
        """last journal name on website
        """
        url = "http://www.code4lib.org/node/86"
        tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        list = tree.find('.//{http://www.w3.org/1999/xhtml}ul')
        names = []
        for name in list:
            names.append(name.text)
        irc.reply(names.pop())
 
    def gc(self,irc,msg,args):
        """google count
        """
        irc.reply(self.count(' '.join(args)))

    def developer(self,irc,msg,args):
        """generate a fantasy developer"""
        attrs = ['Communication', 'BigPicture', 'DetailOriented', 'KungFu', 'GetsStuffDone', 'FlakeFactor']
        dev = ', '.join(["%s:%d" % (attr, self.dnd_attr()) for attr in attrs])
        irc.reply(dev)

    def gamma(self,irc,msg,args):
        """generate a gamma world character"""
        attrs = ['Charisma', 'Constitution', 'Dexterity','Intelligence','Mental Strength','Physical Strength']
        pc = ', '.join(["%s:%d" % (attr, self.dnd_attr()) for attr in attrs])
        irc.reply(pc)

    def dnd(self,irc,msg,args):
        """get a d&d character
        """
        irc.reply("strength:%d dexterity:%d constitution:%d intelligence:%d wisdom:%d charisma:%d" % tuple([self.dnd_attr() for i in range(6)]))
    
    def roll(self, s):
        times, die = map(int, s.split('d'))
        return [randint(1, die) for i in range(times)]
 
    def drop_lowest(self, rolls):
        rolls.remove(min(rolls))
        return rolls
 
    def dnd_attr(self):
        return sum(self.drop_lowest(self.roll('4d6')))

    def duel(self,irc,msg,args):
        if len(args) != 2:
            irc.reply("usage: duel thing1 thing2")
            return
        thing1, thing2 = args
        c1 = self.count(thing1)
        c2 = self.count(thing2)
        if c1 > c2:
            irc.reply("%s wins %i to %i" % (thing1, c1, c2))
        elif c1 < c2:
            irc.reply("%s wins %i to %i" % (thing2, c2, c1))
        else:
            irc.reply("%s and %s tied at %i" % (thing1, thing2, c1))

    def indieduel(self,irc,msg,args):
        if len(args) != 2:
            irc.reply("usage: indieduel thing1 thing2")
            return
        thing1, thing2 = args
        c1 = self.count(thing1)
        c2 = self.count(thing2)
        if c1 > c2:
            irc.reply("%s is too mainstream: %i to %i" % (thing1, c1, c2))
        elif c1 < c2:
            irc.reply("%s is too mainstream: %i to %i" % (thing2, c2, c1))
        else:
            irc.reply("%s and %s tied at %i" % (thing1, thing2, c1))

    def count(self,q):
        q = q.replace('"','')
        q = q.replace("'",'')
        r = google.doGoogleSearch(q)
        self.log.info("searching google for %s" % q)
        return r.meta.estimatedTotalResultsCount

    def library(self,irc,msg,args):
        search_url = 'http://www.librarytechnology.org/lwc-processquery.pl'
        query = {}

        # validate
        if len(args) == 0:
            irc.reply("usage: library [institution_name] [city state [country]]")
            return
       
        if len(args) == 1:
            query['Quick'] = args[0]
        elif len(args) == 2:
            query['City'] = args[0]
            query['State'] = args[1]
        if len(args) == 3:
            query['Country'] = args[2]

        url = search_url + '?' + urlencode(query)
        hits = TidyHTMLTreeBuilder.parse(urlopen(url))
  
        results = []
        for p in hits.findall('.//{http://www.w3.org/1999/xhtml}p'):
            if p.attrib.get('class') == 'listing':
                results.append(self.get_library_detail(p))
        if len(results) == 0:
            irc.reply("game over man!")
        else:
            irc.reply(' ; '.join(results).encode('utf8'))

    def get_library_detail(self,p):
        text = self.get_text(p)
        for a in p.findall('.//{http://www.w3.org/1999/xhtml}a'):
            params = parse_qs(urlparse(a.attrib.get('href'))[4])
            if params.has_key('URL'):
                return text + params['URL'][0]
        return text

    def lurkers(self,irc,msg,args):
        """see who looked at the irc-logs on the web today. use 'all' if 
        you want to see non-resolvable ip addresses
        """
        include_ips = False
        if len(args)>0 and args[0]=='all': include_ips = True
        ips = os.popen("grep 'irc-logs/index.php\?' /var/www/code4lib.org/logs/access_log | cut -f 1 -d ' ' | sort | uniq").read().splitlines()
        resolved = []
        for ip in ips:
          if ip == '': continue
          hostname = os.popen('dnsname %s' % ip).read().strip()
          if hostname == '' and include_ips:
            resolved.append(ip)
          elif hostname:
            resolved.append(hostname)
        resolved.sort()
        irc.reply('; '.join(resolved))

    def rnd(self,irc,msg,args):
        """random page from the wikipedia
        """
        # how awful is this, at least we're working on a DOM ...
        # wikipedia seems to not like the User-Agent of urllib2
        url = 'http://en.wikipedia.org/wiki/Special:Random'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)

        # i tried this beautifulsoup stuff when elementtree was being buggy
        # (http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=461629)  gsf
        html_str = html.read()
        try:
            soup = BeautifulSoup(html_str)
        except UnicodeDecodeError, e:
            raise UnicodeDecodeError, "%s.  HTML was %s." % (e, html_str)
        title = soup.title.string

        def strip_tags(elem):
            text_list = []
            for child in elem.recursiveChildGenerator():
                if isinstance(child, unicode):
                    text_list.append(child)
            return ''.join(text_list)

        text = strip_tags(soup.p)

        link_elem = soup.find('a', title=re.compile('^Permanent link.*'))
        link = link_elem['href'].replace('&amp;', '&')

        irc.reply(("%s : %s <http://en.wikipedia.org%s>" % (title, text, link)).encode('utf-8'))
        
    def hillary(self,irc,msg,args):
        url = 'http://www.hillaryismomjeans.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('a').string)

    def obama(self,irc,msg,args):
        url = 'http://barackobamaisyournewbicycle.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('a').string.strip().upper())

    def isiticedcoffeeweather(self,irc,msg,args):
        if len(args) != 1:
            irc.reply("usage: isiticedcoffeeweather zipcode")
            return
        url = 'http://isiticedcoffeeweather.com/%s' % args[0]
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('h2').string.strip().upper())

    def get_text(self,e):
        string = ''
        if e.text: string += e.text
        for child in e.getchildren():
            string += self.get_text(child)
        if e.tail: string += e.tail
        string = string.replace("\n",'')
        string = re.sub('\+? Details.','', string)
        return string

    def isitfriday(self, irc, msg, args):
#        irc.reply("If it feels like Friday, it's Friday!")
#        return
        isfriday = "nope."
        dow = date.today().weekday()
        if dow == 4:
            isfriday = "yes!"
        irc.reply(isfriday, prefixNick=True)
        return

    def arewethereyet(self, irc, msg, args):
        irc.reply("nope", prefixNick=True)
        return

    def bin2int(self, irc, msg, args, binstring):
        """
        usage: bin2int <bin>
        returns the integer form of a given binary string
        """

        irc.reply(int(binstring, 2), prefixNick=True)
        return

    bin2int = wrap(bin2int, ['text'])

    def nonsense(self, irc, msg, args, nb_words, lang, minl, maxl):
        """
        a generator for pronounceable random words --
        Source: http://ygingras.net/yould --
        Usage: nonsense [num_words] [lang] [min len] [max len] --
        Language codes: en,fr,kjb,fi,nl,de,la
        """
        if nb_words > 10:
            nb_words = 10

        postdata = {}
        postdata['lang'] = lang or 'en'
        postdata['minl'] = minl or 5
        postdata['maxl'] = maxl or 12
        postdata['nb_words'] = nb_words or 1
        postdata = urlencode(postdata)

        try:
            soup = self._url2soup('http://ygingras.net/yould?lang=en', {}, postdata)
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

        words = soup.find('textarea',{'name':'new_domains'}).string.split()
        words = [w.encode('utf-8') for w in words if isinstance(w, unicode)]
        irc.reply(' '.join(words))

    nonsense = wrap(nonsense, [optional('int'),optional('anything'),optional('int'),optional('int')])

    def twit(self, irc, msg, args):
        """
        returns a random tweet from the public timeline
        """

        try:
            soup = self._url2soup('http://twitter.com/statuses/public_timeline.xml')
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

        tweets = soup.findAll('status')
        status = tweets[randint(0, len(tweets)-1)]
        twit = status.user.screen_name.string
        tweet = status.text.string
        irc.reply("%s: %s".encode('utf8', 'ignore') % (twit, tweet))

    def itr(self,irc,msg,args,continent):
        """
        Usage: itr [continent]
        Returns current traffic index from http://internettrafficreport.com/
        Data available for Asia, Australia, Europe, North America and South America
        (default is North America)
        """

        if not continent:
            continent = 'North America'

        try:
            soup = self._url2soup('http://internettrafficreport.com/')
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

        region = None
        for row in soup.find('table', attrs={'border': 1}).findAll('tr'):
            if row.find(text=re.compile(continent,re.I)):
                region = row

        if not region:
            irc.reply("No index for %s" % continent)
            return

        ci = region.contents[1].font.b.string
        art = region.contents[2].font.string
        pl = region.contents[3].font.string
        resp = "ITR for %s: Current Index: %s, Avg Response Time: %s, Avg Packet Loss: %s" % (continent,ci,art,pl)
        irc.reply(resp)

    itr = wrap(itr, [optional('text')])

    def haiku(self, irc, msg, args):
        """
        Random haiku from http://www.vikingmud.org/guilds/samurai/?haiku/random
        """
        soup = self._url2soup('http://www.vikingmud.org/guilds/samurai/?haiku/random')
        main = soup.find('td', {'class': 'main'})
        haiku = main.find('i')
        lmb = lambda s: s.string and s.string.strip() or None
        resp = [lmb(x) for x in haiku.contents]
        irc.reply(' / '.join([x for x in resp if x]), prefixNick=False)

    def zen(self,irc,msg,args):
        """
        returns a random zen proverb from http://oneproverb.net
        """

        try:
            soup = self._url2soup('http://oneproverb.net/cgi-bin/rzp.cgi')
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

        zen = soup.findAll('p')[1].string.strip()
        who = soup.find('span', "who").string.strip()
        who = who.replace('- ', '')
        irc.reply(zen, to=who, prefixNick=True)

    def dance(self, irc, msg, args):
        irc.reply(" o/", prefixNick=False)
        irc.reply("/|", prefixNick=False)
        irc.reply(" >>", prefixNick=False)

    def mf(self, irc, msg, args):
        irc.reply("Hey, " + ' '.join(args) + "...", prefixNick=False)
        irc.reply("    .-. ", prefixNick=False)
        irc.reply("    |-| ", prefixNick=False)
        irc.reply("    | | ", prefixNick=False)
        irc.reply(" _.-|=|-. ", prefixNick=False)
        irc.reply("/ | | | | ", prefixNick=False)
        irc.reply("|       |\ ", prefixNick=False)
        irc.reply("|        / ", prefixNick=False)
        irc.reply(" \     /` ", prefixNick=False)
        irc.reply("  |   |  ", prefixNick=False)

    def halfbaked(self, irc, msg, args):
        """
        returns a radom half-baked idea from http://halfbakery.com
        """
        try:
            soup = self._url2soup('http://www.halfbakery.com/random-idea.html')
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True); return
        except StopParsing, e:
            irc.reply('parsing error %s for %s' % (e.code, url), prefixNick=True); return

        idea = soup.find('a', {'name': 'idea'})
        title = idea.h1.string
        try:
            subtitle = idea.parent.find('font', 'fcl').string
            title = '%s -- %s' % (title, subtitle)
        except:
            pass

        irc.reply(title, prefixNick=True)

    def dow(self, irc, msg, args):
        """
        Get the Dow Jones Industrial Average from teh GOOG
        """
        irc.reply(self._cid_quote(983582,args))

    def nasdaq(self, irc, msg, args):
        """
        Get the NASDAQ from teh GOOG
        """
        irc.reply(self._cid_quote(13756934,args))

    def sandp(self, irc, msg, args):
        """
        Get the S&P from teh GOOG
        """
        irc.reply(self._cid_quote(626307,args))

    def ftse(self, irc, msg, args):
        """
        Get the FTSE from teh GOOG
        """
        irc.reply(self._cid_quote(12590587,args))

    def _cid_quote(self, cid, args):
        directions = { '+' : 'up', '-' : 'down' }
        formats = {
          'def' : "%(idx)s; %(sign)s%(diff)s (%(sign)s%(pct)s)",
          'eng' : "The %(name)s is %(direction)s %(diff)s points (%(pct)s) to %(idx)s."
        }
        try:
          format = formats[args[0].lower()[0:3]]
        except:
          format = formats['def']
        
        # TODO: make this so you can use an ticker
        soup = self._url2soup("http://finance.google.com/finance?cid=%s" % cid)
        data = {}
        try:
            data = {
              'idx' : soup.find(id="ref_%s_l" % cid).string,
              'diff' : soup.find(id="ref_%s_c" % cid).string or '+0',
              'pct' : soup.find(id="ref_%s_cp" % cid).string or '0%',
              'name' : soup.find('h1').string
            }
            data['sign'] = data['diff'][0]
            data['direction'] = directions[data['sign']]
            data['diff'] = data['diff'].strip('+-')
            data['pct'] = data['pct'].strip('()+-')
        except:
            raise
            return 'ruhroh, me no speak google'
        return format % data

    def stock(self, irc, msg, args):
        t = quote(' '.join(args))
        soup = self._url2soup("http://finance.google.com/finance?q=%s" % t)
        match = re.search('var _companyId = (\d+)', str(soup))
        if not match:
            irc.reply("gah, couldn't find stock ticker %s" % t)
            return
        try:
            cid = match.group(1)
            idx = soup.find(id="ref_%s_l" % cid).string.replace('&nbsp;', '')
            p = soup.find(id="ref_%s_cp" % cid).string.replace('&nbsp;', '')
            mktcap = soup.find(id="ref_%s_mc" % cid).string.replace('&nbsp;','')
            pe = soup.find(id="ref_%s_pe" % cid).string.replace('&nbsp;', '')
            hi = soup.find(id="ref_%s_hi" % cid).string.replace('&nbsp;', '')
            lo = soup.find(id="ref_%s_lo" % cid).string.replace('&nbsp;', '')
            hi52 = soup.find(id="ref_%s_hi52" % cid).string.replace('&nbsp;','')
            lo52 = soup.find(id="ref_%s_lo52" % cid).string.replace('&nbsp;','')
            name = ' - '.join(soup.find('title').string.split('-')[0:2]).strip()

            irc.reply("%s - %s %s high:%s low:%s  high52:%s low52:%s p/e:%s mktcap:%s" % (name, idx, p, hi, lo, hi52, lo52, pe, mktcap))
        except:
            irc.reply("ruhroh, me no speak google")

    def prez(self, irc, msg, args):
        """
        Returns expected Presedential race results from http://www.electoral-vote.com/
        """
        irc.reply(self._electoral(0))

    def senate(self, irc, msg, args):
        """
        Returns expected Senate race results from http://www.electoral-vote.com/
        """
        irc.reply(self._electoral(1))

    def house(self, irc, msg, args):
        """
        Returns expected House race results from http://www.electoral-vote.com/
        """
        irc.reply(self._electoral(2))

    def _electoral(self, idx):
        soup = self._url2soup("http://www.electoral-vote.com/")
        dems = soup.findAll('span', {'class':'dem'})
        gops = soup.findAll('span', {'class':'gop'})
        ties = gops[idx].next.next
        return ', '.join([x.string.strip() for x in [dems[idx], gops[idx], ties]])

    def debt(self, irc, msg, args):
        """
        Returns current US gross national debt as
        calculated at http://zfacts.com/p/461.html
        """
        # values taken from http://zfacts.com/giz/G05ndc.js on 2008-10-03
        gndstart = 10124225067127.69
        add_debt_per_year = 676 # in $ billions
        add_debt_per_sec = add_debt_per_year*1000000000/(365*24*60*60)
        from_date = datetime(2008, 10, 01, 11, 0, 0)
        now = datetime.now()
        delta = now - from_date
        add_debt = delta.seconds * add_debt_per_sec
        gnd = gndstart + add_debt
        gnd_str = '%.2f' % gnd
        gnd_whole, gnd_decimal = gnd_str.split('.')
        response = '%sdollars and %scents' % (int2word(gnd_whole),
                int2word(gnd_decimal))
        irc.reply(response)

    def lhc(self, irc, msg, args):
        """
        reports how much time is left until the HLC starts smashing reality^Watoms
        """
        targetdate = datetime(2008, 10, 21, 13, 0, 0)
        now = datetime.now()
        delta = targetdate - now
        irc.reply('%d days left' % delta.days)

    def nytags(self, irc, msg, args, **opts):
        url = 'http://api.nytimes.com/svc/timestags/suggest'
        key = 'aa51418354ed1dc2378f9679a04a0f54:14:13476879'
        q = urlencode({'query': ' '.join(args), 'api-key': key})
        json = urlopen("%s?%s" % (url, q)).read()
        tags = simplejson.loads(json)
        result = ', '.join(tags['results'])
        irc.reply(result)
    
    def flu(self, irc, msg, args, loc):
        """
        Estimate of flu search activity for a given region or location. --
        Usage: flu [location] --
        Enter "list" as location for a list of options ---
        Data from http://www.google.org/flutrends/
        """
        try:
            reader = csv.reader(urlopen("http://www.google.org/flutrends/data.txt"))
        except:
            print "Error fetching flu data: ", sys.exc_info()[0]
        data = [row for row in reader if len(row) > 2]
        locations = [x.lower() for x in data[0][1:]]
        if loc == 'list':
            resp = ', '.join(locations)
            irc.reply(resp)
            return
        latest_data = ["%.2f" % float(x) for x in data[-1][1:]]
        previous_data = ["%.2f" % float(x) for x in data[-2][1:]]
        latest = dict(zip(locations, latest_data))
        previous = dict(zip(locations, previous_data))
        if loc.lower() not in latest:
            irc.reply("No data for location: %s" % loc)
        else:
            trend = cmp(latest[loc.lower()], previous[loc.lower()])
            if trend < 0:
                trend = 'down'
            elif trend == 0:
                trend = 'stable'
            else:
                trend = 'up'
            resp = "As of %s the flu search activity index for %s was %s; trend is %s" \
                % (data[-1][0], loc, latest[loc.lower()], trend)
            irc.reply(resp)
    
    flu = wrap(flu, ['text'])

    def orsome(self, irc, msg, args, splitter, s):
        """Usage: orsome [/separator/] string"""
        if not s:
            return
        if splitter:
            items = [x.strip() for x in re.split(splitter, s)]
        else:
            items = [x.strip() for x in re.split('\s+', s)]
        irc.reply(' or '.join(items), prefixNick=False)
         
    orsome = wrap(orsome, [optional('regexpMatcher'), 'text'])

    def decide(self, irc, msg, args, choices):
        pattern = re.compile('\s+or\s+', re.I)
        clist = re.split(pattern, choices)
        if randint(0, 10) == 0:
            irc.reply("That's a tough one...")
            return
        irc.reply("go with " + clist[randint(0, len(clist)-1)])

    decide = wrap(decide, ['text'])

    def _url2soup(self, url, qsdata={}, postdata=None, headers={}):
        """
        Fetch a url and BeautifulSoup-ify the returned doc
        """
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        headers.update({'User-Agent': ua})
        params = urlencode(qsdata)
        if params:
            if '?' in url:
                url = "%s&%s" % (url,params)
            else:
                url = "%s?%s" % (url,params)
        req = Request(url,postdata,headers)
        doc = urlopen(req)
        data = doc.read()
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        return soup

    def bartender(self, irc, msg, args):
        """
        pours a beer from http://web.mit.edu/~tcarlile/www/beer/beerlist.html
        for you
        """
        soup = self._url2soup('http://web.mit.edu/~tcarlile/www/beer/beerlist.html')
        beers = []
        for li in soup.findAll('li'):
            if li.a:
                beers.append((li.a['href'], li.a.string))
        beer = beers[randint(0, len(beers))]
        irc.reply("fills a pint glass with %s, and sends it sliding down the bar to %s (%s)" % (beer[1], msg.nick, beer[0]), action=True)

    def anon(self, irc, msg, args):
        """
        Spits out random nonsense from 'anon,' that loveable idiot of a troll
        """
        trolls = ["Hey Roy, get a life.",
                  "Did OCLC put co-option of code4lib in your performance review for 2009?",
                  "you don't belong to code4lib, since you acted in an unwelcome fashion there and were shunned accordingly.",
                  "How about enabling comments over on your site, Winer of the library world?",
                  "Roy's a big boy--think he can speak to OCLC's desire to act like Microsoft and assert dominance over an informal organization",
                  "Follow the money on the code4libcon Google group",
                  "Awesome, hypocrisy.",
                  "Let's say that OCLC and code4lib is about as awesome as DSpace plus HP.",
                  "OCLC as largest code4lib sponsor=death",
                  "Roy as OCLC shill=shame for LJ and code4lib",
                  "Roy=saint, or Joe of Arc since leaving CDL?",
                  "court fool of the library world",
                  "aren't you on strike or something?",
                  "Hey Roy, what does OCLC think about code4lib?",
                  "the community voted the ridiculous Ohio location down, so it does know what sponsorship is, indeed",
                  "Isn't Ohio the state that doesn't know the difference between a business and a non-profit cooperative?",
                  "OCLC is using Roy and its money to influence a loose collective in the process of expanding.",
                  "are you affiliated with OCLC?",
                  "But you don't now--you're a vendor.",
                  "May as well post an OCLC ad, since you're shilling for their services in your presentation.",
                  "Oh, does this benefit WorldCat Local?",
                  "RFP's exist because libraries are public. The Oh Can Libraries Concede trust would prefer otherwise, I'm sure",
                  "if channels matter, then why not community dot oclc dot org slash roy?",
        ]
        troll = trolls[randint(0, len(trolls)-1)]
        irc.reply(troll, prefixNick=True)

    def _diebold_tallies(self, tally='', year=''):
        """ Gets a tally from the diebold-o-tron """
        base_url = 'http://vote.code4lib.org/election/results/'
        tallies = {
            'keynotes': {'2009': '4'},
            'necode4lib': {'2008': '5'},
            'hosts': {'2009': '3'},
            'talks': {'2008': '2', 
                      '2009': '7'},
            'logo': {'2008': '6'}
        }
        try:
            poll_number = tallies[tally][year]
        except KeyError:
            raise PollNotFoundException("tally or year not found")
        poll_url = base_url + poll_number
        from socket import setdefaulttimeout
        setdefaulttimeout(60)
        try:
            json = urlopen(Request(poll_url, None, {'Accept': 'application/json'})).read()
        except HTTPError, e:
            raise PollNotFoundException("%s" % e)
        json = re.sub(r'\\[0-9A-fa-f]{3}', '', json)
        try:
            votes = simplejson.loads(json)
        except UnicodeDecodeError:
            votes = simplejson.loads(json.decode('ascii', 'ignore'))
        tallies = []
        for count in votes:
            vote_getters = votes[count]
            for vote_getter in vote_getters:
                tallies.append((vote_getter['attributes']['name'], count))
        tallies.sort(lambda a,b: cmp(int(b[1]), int(a[1])))
        return tallies

    def talks2009(self, irc, msg, args):
        """ 
        Gets tally of talk votes for 2009 conference
        """
        try:
            tallies = self._diebold_tallies("talks", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))

    def bubble2009(self, irc, msg, args):
        """ 
        List talks that are within 4 ranks of the cutoff range for the 2009 conference
        """
        cutoff = 22
        try:
            tallies = self._diebold_tallies("talks", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies[cutoff-3:cutoff+2])).encode('utf-8'))

    def talks2008(self, irc, msg, args):
        """ 
        Gets tally of talk votes for 2008 conference
        """
        try:
            tallies = self._diebold_tallies("talks", "2008")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for talk votes in 2008: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))


    def logo2008(self, irc, msg, args):
        """ 
        Gets tally of logo votes for 2008
        """
        try:
            tallies = self._diebold_tallies("logo", "2008")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for logos in 2008: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))


    def hosts2009(self, irc, msg, args):
        """ 
        Gets tally of host votes for 2009 conference
        """
        try:
            tallies = self._diebold_tallies("hosts", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for hosts in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))


    def keynotes2009(self, irc, msg, args):
        """ 
        Gets tally of keynoter votes for 2009 conference
        """
        try:
            tallies = self._diebold_tallies("keynotes", "2009")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for keynotes in 2009: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))


    def necode4lib(self, irc, msg, args):
        """ 
        Gets tally of location votes for 2008 New England code4lib conference 
        """
        try:
            tallies = self._diebold_tallies("necode4lib", "2008")
        except PollNotFoundException, pnfe:
            irc.reply("Poll not found for necode4lib in 2008: %s" % pnfe)
        else:
            irc.reply(('; '.join("%s [%s]" % t for t in tallies)).encode('utf-8'))


Class = Assorted


