from urllib import quote
from urllib2 import urlopen, Request

import supybot.callbacks as callbacks
from supybot.commands import *
from BeautifulSoup import BeautifulSoup as BS

class Delicious(callbacks.Privmsg):

    def fauxonomy(self,irc,msg,args):
        """get tags associated with a url
        """
        url = quote(args[0])
        conn = urlopen('http://badges.del.icio.us/feeds/json/url/data?url=%s' 
            % url)
        response = eval(conn.read())
        if len(response) == 0:
          irc.reply("site doesn't appear to be in delicious")
          return
        total_posts = response[0]['total_posts']
        tag_stats = response[0]['top_tags']
        tags = tag_stats.keys()
        tags.sort(lambda a,b: cmp(tag_stats[b], tag_stats[a]))
        msg = ' ; '.join(map(lambda tag: "%s:%i" % (tag, tag_stats[tag]), tags))
        irc.reply("[%i posts] %s" % (total_posts, msg))

    def tagspark(self, irc, msg, args):
        """
        Usage: tagspark tag querytag --
        Returns a sparkline-ish string indicating how often items recently
        tagged with 'tag' were also tagged with 'querytag' (on del.icio.us)
        """
        tag = args.pop(0)

        if not args:
            irc.reply("Usage: tagspark tag querytag")
            return
        querytag = args.pop(0)

        url = 'http://del.icio.us/rss/tag/%s' % tag.lower()
        conn = urlopen(url)
        soup = BS(conn)
        items = soup('item')

        if not items:
            irc.reply('No results')
            return

        def hit(item, tag):
            subject = item.find('dc:subject')
            if subject:
                othertags = subject.string.lower().split()
                if querytag.lower() in othertags:
                    return '|'
            return '.'

        spark = ''.join([hit(i, querytag) for i in items])
        irc.reply(spark, prefixNick=True)

    def tagcount(self, irc, msg, args, tag):
        """
        Usage: @tagcount tag /
        Returns counts for adjacent tags based on from delicious.com/popular bookmarks
        """
        url = 'http://del.icio.us/rss/tag/%s' % tag.lower()
        conn = urlopen(url)
        soup = BS(conn)
        items = soup('item')

        if not items:
            irc.reply('No results')
            return

        counts = {}
        for i in items:
            subject = i.find('dc:subject')
            if subject:
                for t in subject.string.lower().split():
                    if t != tag:
                        counts[t] = counts.get(t, 0) + 1

        sorted_counts = sorted(counts.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        resp = ', '.join(["%s: %d" % (k, v) for (k, v) in sorted_counts][:20])
        irc.reply(resp, prefixNick=True)

    tagcount = wrap(tagcount, ['text'])


Class = Delicious
