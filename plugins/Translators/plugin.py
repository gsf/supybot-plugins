# coding: utf-8
import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re
from random import randint, randrange, choice
import supybot.utils.web as web
import BeautifulSoup as BS
from urllib import urlencode
from os.path import join, dirname, abspath
import _pairtree

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Sing Plugin; http://code4lib.org/irc)')
STOPWORDS = open(join(dirname(abspath(__file__)), 'stopwords.txt')).read().split()

class Translators(callbacks.Privmsg):
    def canuck(self, irc, msg, args):
        """ string
        Translates text into a Canadian dialect
        """
        text = ' '.join(args).strip()
        text = re.sub(r'z', 'zed', text)
        text = re.sub(r'(\w)or', r'\1our', text)
        text = re.sub(r'gray', 'gray', text)
        text = re.sub(r'catalog(?![ui])', 'catalogue\1', text)
        # commenting these out for now since they make output from Weather ugly
        #text = re.sub(r'(24|twenty.four)', 'two-four', text)
        #text = re.sub(r'(6|six)', 'six-pack', text)
        text = re.sub(r'out', 'oat', text)
        text = re.sub(r'ouch', 'oach', text)
        text = re.sub(r'ache', 'awchee', text)
        matches = re.findall(r'((-?\d+)(\.\d+)?.F)', text)
        for match in matches:
            ftemp = float(match[1] + match[2])
            celsius = (ftemp - 32) * 5 / 9
            text = re.sub(match[0], "%-3.1fC" % celsius, text)
        irc.reply(text + ", eh?", prefixNick=True)
    
    def aussie(self, irc, msg, args):
        """ string
        Translates string into Australian English Vernacular
        """
        irc.reply("SHRIMP ON THE BARBIE, MATES!", prefixNick=True)
    
    def viking(self, irc, msg, args):
        """ string
        Translates string into Viking
        """
        irc.reply("SKÅL!", prefixNick=True)
    
    def lbjay(self, irc, msg, args):
        """ string
        Offer some constructive criticism
        """
        irc.reply("%s: PLEASE TRY HARDER" % ' '.join(args), prefixNick=False)
    
    def ircnickize(self, irc, msg, args):
        """ string
        Normalizes a string per irc nick rules
        """
        nick = ''
        for arg in args:
            for s in arg.split():
                nick += s
        # strip out all non-word characters to make freenode happy
        nick = re.compile(r'\W', re.I).sub('', nick)
        # string slice used because freenode restricts >16-char nicks
        irc.reply(nick[0:15], prefixNick=False)
    
    def mccainize(self, irc, msg, args):
        """
        Translates text into McCain speechifyin'
        """
        prefix = "My friends, " if randint(0,2) else "My fellow prisoners, "
        irc.reply(prefix + ' '.join(args), prefixNick=True)
    
    def homelessorcode4libber(self, irc, msg, args):
        """
        Determines whether someone is homeless or a code4libber
        """
	what = ['homeless', 'code4libber', 'WEREWOLF!']
        irc.reply('%s = %s'% (' '.join(args), what[randint(0,2)]), prefixNick=False)
    
    def dick(self, irc, msg, args):
        """
        Disclaims your desire to be a dick
        """
        irc.reply("I don't mean to be a dick, but " + ' '.join(args), prefixNick=True)
    
    def edsu(self, irc, msg, args):
        """
        States edsu's attitude on selfsame plugin command
        """
        irc.reply("let me remind you people, " + ' '.join(args), prefixNick=True)
    
    def rsinger(self, irc, msg, args):
        """
        Ross gives you some advice.
        """
        irc.reply("PLATFORM " * len(args), prefixNick=True)
    
    def kgs(self, irc, msg, args):
        """
        bad kgs imitation
        """
        irc.reply("nosrsly, " + ' '.join(args), prefixNick=True)

    def rob(self, irc, msg, args):
        """
        Rob says what you want him to say. Kinda.
        """
        text = ' '.join(args).split(' ')
        if len(text) < 2:
          irc.reply('... Wait, what?')
        else:
          phrase = text[0:randint(1,len(text)-1)]
          irc.reply(' '.join(phrase) + '... Wait, what?')

    def obamit(self, irc, msg, args):
        """
        Garners attention for your statements in a folksy way
        """
        look = "Look, " if randint(0,1) else "Look, here's what I'm saying... "
        irc.reply(look + ' '.join(args))
    
    def mjg(self, irc, msg, args):
        """
        Truncates and refocuses your statement
        """
        s = ' '.join(args)
        high = len(s)
        low = min(7, high-1)
        irc.reply("%s... OMG! Bacon!" % s[0:randint(low,high)])
    
    def embed(self, irc, msg, args):
        """
        Adds "in bed" to the end of a phrase.
        """
        s = ' '.join(args).strip(".")
        
        motivate = re.match(r'^(.*) - (.*)$', s)
        quote = re.match(r'^Quote #(\d+): "(.*)" \((.*)\)$', s)
        if motivate:
            msg = "%s ... in bed - %s" % (motivate.group(1), motivate.group(2))
        elif quote:
            msg = 'Quote #%sa "%s ... in bed" - (%s)' % quote.groups()
        else:
            msg = "%s ... in bed." % s
        
        irc.reply(msg)
    
    def scalia(self, irc, msg, args):
        """<string>
        random 'scare' quote insertion"""
        if len(args) == 0:
            irc.reply("try providing some text, morno")
            return
        words = []
        token_positions = []
        i = 0
        for arg in args:
            for s in arg.split():
                words.append(s)
                if s.strip(r'`!()-{}[]<>"\':;.,?').lower() not in STOPWORDS:
                    token_positions.append(i)
                i += 1
        try:
            randidx = randrange(len(token_positions))
            words[token_positions[randidx]] = "'%s'" % words[token_positions[randidx]]
        except:
            # all stopwords
            pass
        irc.reply(' '.join(words))
    
    def chef(self, irc, msg, args):
        """BORK! BORK! BORK!"""
        self._chefjivevalleypig(irc, 'chef', ' '.join(args))
    
    def jive(self, irc, msg, args):
        """Like, yeah..."""
        self._chefjivevalleypig(irc, 'jive', ' '.join(args))
    
    def valley(self, irc, msg, args):
        """Fer sure!"""
        self._chefjivevalleypig(irc, 'valspeak', ' '.join(args))
    
    def igpay(self, irc, msg, args):
        """Ustjay utwhay ouyay inkthay"""
        self._chefjivevalleypig(irc, 'piglatin', ' '.join(args))
    
    def _chefjivevalleypig(self, irc, type, s):
        params = urlencode(dict(input=s,type=type))
        url = 'http://www.cs.utexas.edu/users/jbc/bork/bork.cgi?' + params
        resp = web.getUrl(url, headers=HEADERS)
        resp = re.sub('\n', ' ', resp)
        irc.reply(resp.encode('utf-8', 'ignore').strip())

    
    def sabram(self, irc, msg, args):
        """ [<text>]
        Get @sabram to falsely attribute a quote to Cliff!
        """
        template = '<sabram> Cliff said: "%s"'
        if args:
            irc.reply(template % ' '.join(args))
            return
        url = "http://www.ivyjoy.com/quote.shtml"
        try:
            resp = web.getUrl(url, headers={'User-agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13'})
            soup = BS.BeautifulSoup(resp)
            quotation = soup.find('font').contents[0].strip()
        except:
            irc.reply(template % "Some stupid error occurred")
        irc.reply(template % quotation, prefixNick=False)
    
    def drunk(self, irc, msg, s):
        params = urlencode(dict(text=s,voice='drunk'))
        url = 'http://www.thevoicesofmany.com/text.php?' + params
        resp = web.getUrl(url, headers=HEADERS)
        soup = BS.BeautifulSoup(resp)
        try:
            translated = soup.find('td', id='top').blockquote.string
        except:
            irc.reply("oops, didn't work")
        irc.reply(resp.encode('utf-8', 'ignore').strip())
    
    def takify(self, irc, msg, args):
        """ĆẪṖĨṰĄŁȊȤḖŜ ĀÑƊ ȂḒƉŜ ȒẬÑḊỎḾ ḒÎḀĊṘĨŤİČṦ ƮǬ Ȁ ŞƮṞƗṆƓ Ȭℱ ƮỆẊṮ"""
        variants = {
            'A' : u'ÀÁÂÃĀĂȦÄẢÅǍȀȂĄẠḀẦẤẪẨẰẮẴẲǠǞǺẬẶ',
            'B' : u'ḂƁḄḆℬ',
            'C' : u'ĆĈĊČƇÇḈ©',
            'D' : u'ḊƊḌḎḐḒĎĐƉↁ',
            'E' : u'ÈÉÊẼĒĔĖËẺĚȄȆẸȨĘḘḚỀẾỄỂḔḖỆḜℰℇƎ',
            'F' : u'ḞƑℱℲ',
            'G' : u'ǴĜḠĞĠǦƓĢǤ',
            'H' : u'ĤḢḦȞǶḤḨḪĦℋℍ',
            'I' : u'ÌÍÎĨĪĬİÏỈǏỊĮȈȊḬƗḮ',
            'J' : u'Ĵ',
            'K' : u'ḰǨḴƘḲĶK',
            'L' : u'ĹḺḶĻḼĽĿŁḸℒ',
            'M' : u'ḾṀṂℳ',
            'N' : u'ǸŃÑṄŇŊƝṆŅṊṈ',
            'O' : u'ÒÓÔÕŌŎȮÖỎŐǑȌȎƠǪỌƟØỒỐỖỔȰȪȬṌṎṐṒỜỚỠỞỢǬỘǾ',
            'P' : u'ṔṖƤ℗ℙ',
            'Q' : u'Ԛ℺ℚ',
            'R' : u'ŔṘŘȐȒṚŖṞṜƦ®ℝℛℜ℟',
            'S' : u'ŚŜṠŠṢȘŞṤṦṨ',
            'T' : u'ṪŤƬƮṬȚŢṰṮŦ',
            'U' : u'ÙÚÛŨŪŬÜỦŮŰǓȔȖƯỤṲŲṶṴṸṺǛǗǕǙỪỨỮỬỰ',
            'V' : u'ṼṾ℣',
            'W' : u'ẀẂŴẆẄẈ',
            'X' : u'ẊẌ',
            'Y' : u'ỲÝŶỸȲẎŸỶƳỴ',
            'Z' : u'ŹẐŻŽȤẒẔƵ'
        }
        
        source = u' '.join([arg.decode('utf8') for arg in args]).upper()
        result = []
        for letter in source:
            try:
                possibles = variants[letter]
            except KeyError:
                possibles = [letter]
            result.append(possibles[randrange(len(possibles))])
        response = u' '.join(result)
        irc.reply(response.encode('utf8', 'ignore'), prefixNick=False)
    
    def foxnews(self, irc, msg, args, text):
        """ <text>
        Use nebulous sources to present your own screwed-up viewpoint!
        """
        variants = [
            'Sources claim',
            'In fact, some have said',
            'Can you deny the rumors',
            'Official sources have yet to deny',
            ]
        variant = variants[randrange(len(variants))]
        irc.reply('%s that %s' % (variant, text), prefixNick=False)
    
    foxnews = wrap(foxnews, ['text'])
    
    def snowman(self, irc, msg, args):
        """ <text>
        UNICODE SNOWMAN ALL UP IN YA TEXT BRAW
        """
        words = [arg.decode('utf8') for arg in args]
        snowords = [u'☃' + u'☃'.join(list(word)) for word in words]
        response = u' '.join(snowords)
        irc.reply(response.encode('utf8', 'ignore'), prefixNick=False)
    
    def danify(self, irc, msg, args):
        """<first> <last>
        Danify your name
        """
        variants = { 'a': u'å', 'e': u'è', 'i': u'Ḯ', 'o': u'ø', 'u': u'ü' }
        words = [arg.decode('utf8') for arg in args]
        danewords = []
        for w in words:
            for k, v in variants.items():
                w = w.lower().replace(k, v)
            danewords.append(w.capitalize())
        response = ' '.join(danewords)
        response += 'sen'
        irc.reply(response.encode('utf-8', 'ignore'))
    
    def horatio(self, irc, msg, args):
        """ <text>
        make it sound like you're Horatio Caine from CSI, complete w/ The Who and sunglasses"""
        intros = ['looks like',
            'sounds like',
            'it appears that',
            'on the other hand,',
            'i guess you could say',
            'you might want to consider that',]
        words = args
        if len(words) == 1:
            words = (' '.join(words)).split()
        r1 = u'( ಠ_ಠ) ' + choice(intros) + u' ' + words[0]
        irc.reply(r1.encode('utf-8', 'ignore'), prefixNick=False)
        irc.reply(u'( ಠ_ಠ)>--■-■'.encode('utf-8','ignore'), prefixNick=False)
        r2 = u'(-■_■) ' + ' '.join(words[1:])
        irc.reply(r2.encode('utf-8', 'ignore'), prefixNick=False)
        irc.reply('YEAAAAAAAAAAAAAAAAAAAAAAH', prefixNick=False)

    def pairtree(self, irc, msg, args, id):
        """<id>
        Generate a pairtree based on the given ID.
        """
        irc.reply('/'.join(_pairtree.id_to_path(id)))
    
    pairtree = wrap(pairtree,['text'])
    
    def zalgo(self, irc, msg, args, opts, text):
        """[--intensity 1-200] text
        ZALGO"""
        zalgo_threshold = 50
        for opt, arg in opts:
            if opt == 'intensity':
                if arg in range(1,201):
                    zalgo_threshold = arg
        zalgo_chars = [unichr(i) for i in range(0x0300, 0x036F + 1)]
        zalgo_chars.extend([u'\u0488', u'\u0489'])
        random_extras = [unichr(i) for i in range(0x1D023, 0x1D045 + 1)]
        def insert_randoms(text):
            newtext = []
            for char in text:
                newtext.append(char)
                if randint(1,5) == 1:
                    newtext.append(choice(random_extras))
            return u''.join(newtext)
        source = insert_randoms(text.decode('utf8').upper())
        zalgoized = []
        for letter in source:
            zalgoized.append(letter)
            zalgo_num = randint(0, zalgo_threshold) + 1
            for _ in range(zalgo_num):
                zalgoized.append(choice(zalgo_chars))
        response = choice(zalgo_chars).join(zalgoized)
        irc.reply(response.encode('utf8', 'ignore'), prefixNick=False)
    
    zalgo = wrap(zalgo, [getopts({'intensity':'int'}), 'text'])
    
    def platform(self, irc, msg, args):
      irc.reply("HOW MANY %s CAN I PUT YOU DOWN FOR?" % (' '.join(args).upper()), prefixNick=False)
    platforms = platform
    
    def gosling(self, irc, msg, args):
      """ <text> - talk like ryan gosling"""
      irc.reply("Hey girl. %s" % (' '.join(args)), prefixNick=False)

Class = Translators


