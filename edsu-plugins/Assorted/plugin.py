from supybot.commands import *
import supybot.callbacks as callbacks

import os
import re
from elementtidy import TidyHTMLTreeBuilder
from urllib2 import urlopen, urlparse, Request, build_opener, HTTPError
from urllib import quote, urlencode
from urlparse import urlparse
from cgi import parse_qs
from random import randint
from re import sub, match
import feedparser
import google
import simplejson
from BeautifulSoup import BeautifulSoup, StopParsing
from datetime import date

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

    def votes2008(self,irc,msg,args):
      """polls code4libcon 2008 votes
      """
      from socket import setdefaulttimeout
      setdefaulttimeout(60)
      url = 'http://dilettantes.code4lib.org:6789/election/results/2'
      json = urlopen(Request(url, None, {'Accept': 'application/json'})).read()
      json = sub(r'\\[0-9A-fa-f]{3}', '', json)
      json = json.decode('utf-8', 'ignore')
      votes = simplejson.loads(json)

      tallies = []
      for count in votes:
        talks = votes[count]
        for talk in talks:
          tallies.append((talk['attributes']['name'], count))

      tallies.sort(lambda a,b: cmp(int(b[1]), int(a[1])))
      def fmt(t): return "%s [%s]" % t

      if len(args) > 0:
        try:
          spot = int(args[0]) - 1
          if spot < 0 or spot >= len(tallies):
            raise "whatevah"
          irc.reply("%s - %s".encode('utf8') % (tallies[spot][0]))
        except:
          irc.reply('try again d00d')
        return

      msg = '; '.join(fmt(t) for t in tallies[0:17])
      msg += '  --------  ' 
      msg += '; '.join(fmt(t) for t in tallies[18:])
      irc.reply(msg.encode('utf-8'))

    def hosts2009(self,irc,msg,args):
      """hosts vote for 2009
      """
      url = 'http://dilettantes.code4lib.org:6789/election/results/3'
      json = urlopen(Request(url, None, {'Accept': 'application/json'})).read()
      json = sub(r'\\[0-9A-fa-f]{3}', '', json)
      votes = simplejson.loads(json)
      tallies = []
      for count in votes:
        venues = votes[count]
        for venue in venues:
          tallies.append((venue['attributes']['name'], count))
      tallies.sort(lambda a,b: cmp(int(b[1]), int(a[1])))
      def fmt(t): return "%s [%s]" % t
      irc.reply(('; '.join(fmt(t) for t in tallies)).encode('utf-8'))

    def hosts2010(self,irc,msg,args):
      """votes for the 2010 code4libcon ; courtesy of 
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
          if brief and not match('http', talk_name):
            talk_name = sub('( -|[:/.]).*', '', talk_name)
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

    def band(self,irc,msg,args):
        """band

        Get a band name from dchud's list
        """

        url = "http://www-personal.umich.edu/~dchud/fng/names.html"
        ## content from url is not well-formed, so switching to 
        ## beautifulsoup, mjg
        #tree = TidyHTMLTreeBuilder.parse(urlopen(url))
        #pre = tree.find('.//{http://www.w3.org/1999/xhtml}pre')
        #bands = pre.text.split("\n")
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        soup = BeautifulSoup(html.read())
        pre = soup.find('pre')
        bands = pre.string.split("\n")
        band = bands[randint(0,len(bands)-1)]
        irc.reply(band)

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
        soup = BeautifulSoup(html_str)
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

        #tree = TidyHTMLTreeBuilder.parse(html)
        #ns = {'ns': 'http://www.w3.org/1999/xhtml'}
        #
        #title = self.get_text(tree.findall('.//{%(ns)s}title' % ns)[0]).split(' - ')[0]
        #xpath = './/{%(ns)s}body/{%(ns)s}div/{%(ns)s}div/{%(ns)s}div/{%(ns)s}div/{%(ns)s}p' % ns
        #text = self.get_text(tree.findall(xpath)[0])

        #link = ''
        #for a in tree.findall('.//{%(ns)s}a' % ns):
        #    if a.attrib.get('title','').startswith('Permanent link'):
        #        link = a.attrib['href']

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


    def get_text(self,e):
        string = ''
        if e.text: string += e.text
        for child in e.getchildren():
            string += self.get_text(child)
        if e.tail: string += e.tail
        string = string.replace("\n",'')
        string = sub('\+? Details.','', string)
        return string

    def isitfriday(self, irc, msg, args):
        irc.reply("If it feels like Friday, it's Friday!")
        return
#        isfriday = "nope."
#        dow = date.today().weekday()
#        if dow == 4:
#            isfriday = "yes!"
#        irc.reply(isfriday, prefixNick=True)
#        return

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
        irc.reply("%s: %s" % (twit, tweet))

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
        title = idea.font.string
        try:
            subtitle = idea.parent.findAll('font')[1].string
            title = '%s -- %s' % (title, subtitle)
        except:
            pass

        irc.reply(title, prefixNick=True)

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
        soup = BeautifulSoup(data, convertEntities=['html','xml'])
        return soup

Class = Assorted


