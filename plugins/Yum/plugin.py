###
# TODO: 
# * add searching for allrecipes and recipezaar
# * add yelp restaurant reviews by zipcode

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
import urllib
import re
import copy
from urllib2 import Request, build_opener, HTTPError
from string import capwords
from random import randint

class Yum(callbacks.Plugin):
    """
    Add the help for "@plugin help Yum" here
    This should describe *how* to use this plugin.
    """
    threaded = True

    def __init__(self,irc):
        self.__parent = super(Yum, self)
        self.__parent.__init__(irc)
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        self.opener = build_opener()
        self.opener.addheaders = [('User-Agent', ua)]

    def tinyurl(self, url):
        r = Request('http://tinyurl.com/api-create.php?url=%s' % url)
        doc = self.opener.open(r)
        soup = BeautifulSoup(doc)
        return str(soup)

    def _get_soup(self, irc, url, postdata=None, headers={}):
        # stole this from robcaSSon's traffic plugin so blame him
        doc = None
        req = Request(url, postdata)

        try:
            doc = self.opener.open(req)
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True)
            return

        html = doc.read()
        myMassage = copy.copy(BeautifulSoup.MARKUP_MASSAGE)
        myMassage.extend([(re.compile('<!-([^-])'), lambda match: '<!--' + match.group(1))])
        soup = BeautifulSoup(html, markupMassage=myMassage)
        return soup

    def recipe(self, irc, msg, args):
        """
        Returns the first result of a recipe search at epicurious.com
        """
        if len(args) == 0:
            irc.reply('usage: recipe keyword [keyword...] [count (default:1)]')
            return 

        ret_count = 1
        if args[-1].isdigit():
            ret_count = int(args.pop(-1))

        if ret_count > 3:
            ret_count = 3
            irc.reply('(max return count is 3)', prefixNick=True)

        baseurl = 'http://epicurious.com'
        query = '+'.join(map(urllib.quote, args))
        url = '%s/tools/searchresults?type=advanced&operator=All&search=%s' % (baseurl,query)
        soup = self._get_soup(irc, url)

        recipes = soup.findAll('a', "hed")[0:ret_count]
        results = []
        for r in recipes:
            recTitle = r.string 

            if not recTitle:
                recTitle = r.contents[0]
                recTitle = re.sub('\(', '', recTitle)

            recHref = r['href']
            recipeUrl = self.tinyurl(baseurl + recHref)
            results.append("%s (%s)" % (recTitle.capitalize(), recipeUrl))

        if len(results) == 0:
            irc.reply('no results!', prefixNick=True)
            return

        irc.reply(' ; '.join(results), prefixNick=True)
        return

    def noodlr(self, irc, msg, args):
        """
        get ideas for noodles from noodlr.net
        """
        url = "http://noodlr.net/"
        if len(args) <= 1:
            if args[0] == "vegetarian":
                postdata = {"vegetarian": "true"}
            noodles = self._get_soup(url, postdata=postdata)
            irc.reply(noodles.find('p', attrs={"id": "soup"}), prefixNick=True)
        else:
            irc.reply("usage: noodlr [vegetarian]", prefixNick=True)

    def calories(self, irc, msg, args):
        """
        Returns the calories for a given food item. Calorie figures
        are obtained from http://calorie-count.com
        """
        if len(args) == 0:
            irc.reply('usage: calories <something edible>')
            return 

        baseurl = 'http://www.calorie-count.com'
        query = '+'.join(args)
        params = urllib.urlencode({'search_type': 'foods', 'generic': 1, 'searchpro': query})
        url = '%s/calories/search.php?%s' % (baseurl, params)
        soup = self._get_soup(irc, url)

        results = soup('a', href=re.compile('\/calories\/item\/\d+.html'))
        hits = len(results)
        if hits == 0:
            irc.reply('no results!', prefixNick=True)
            return

        match = results[0]['href']
        url = '%s%s' % (baseurl, match)
        soup = self._get_soup(irc, url)
        
        serving_size = 'unknown'
        nutrition = soup.find('div', id="nutritionfacts")
        sizes = nutrition.findAll('option')
        if len(sizes) > 0:
            serving_size = sizes[-1].string

        title = soup.html.head.title
        calories = nutrition.find(text=re.compile('^Calories')).findNext('div').string

        resp = '%s %s (serving size: %s) - %s' % (calories, title.string, serving_size, url)
        irc.reply(resp, prefixNick=True)
        return

    def beerme(self, irc, msg, args, q):
        """
        Usage: beerme [keywords]
        Returns a random beer from search results of http://whatalesyou.com
        """
        if not q:
            q = 'beer'
        searchuri = 'http://www.whatalesyou.com/beersearch.asp'
        postdata = urllib.urlencode({ 'submit2': 'Search', 'beer': q })
        soup = self._get_soup(irc, searchuri, postdata)
        results = soup.findAll('a', href=re.compile('beerdetail1.asp'))

        hits = len(results)
        if hits == 0:
            irc.reply('no results!', prefixNick=True)
            return

        randresult = results[randint(0, hits - 1)]
        beerid = re.search('(\d+)$', randresult['href']).group(0)
        if not beerid:
            irc.reply('no results!', prefixNick=True)
            return

        beerUrl = 'http://www.whatalesyou.com/beerdetail1.asp?ID=%s' % beerid
        soup = self._get_soup(irc, beerUrl)
        beernameTd = soup.find('td', colspan=6)
        beerName = beernameTd.find('font').string.strip()
        breweryTd = beernameTd.parent.nextSibling.nextSibling.nextSibling.nextSibling.find('td')
        breweryName = breweryTd.findAll('font')[1].string.strip()

        sug = ['Enjoy','How about','Here\'s','You might like','Try', 'Wet your whistle with']
        article = 'a'
        if "aeiou".find(beerName[:1].lower()) != -1:
            article = 'an'

        resp = "%s %s %s by %s - %s" % (sug[randint(0, len(sug)-1)], article, beerName, breweryName, self.tinyurl(beerUrl))
        irc.reply(resp, prefixNick=True)

    beerme = wrap(beerme, [optional('text')])
            
Class = Yum
