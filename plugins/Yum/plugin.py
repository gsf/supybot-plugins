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
from urllib2 import build_opener, HTTPError
from string import capwords

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

    def _get_soup(self, irc, url):
        # stole this from robcaSSon's traffic plugin so blame him
        doc = None
        try:
            doc = self.opener.open(url)
        except HTTPError, e:
            irc.reply('http error %s for %s' % (e.code, url), prefixNick=True)
            return
        xhtml_str = doc.read()
        soup = BeautifulSoup(xhtml_str)
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
            results.append("%s (%s%s)" % (recTitle.capitalize(), baseurl, recHref))

        if len(results) == 0:
            irc.reply('no results!', prefixNick=True)
            return

        irc.reply(' ; '.join(results), prefixNick=True)
        return

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

Class = Yum
