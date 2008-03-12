import supybot
import feedparser
import urllib2
import re

def strip(s):
    return re.sub('</?.+?>', '', s)

class LibraryThing(supybot.callbacks.Privmsg):

    def bookevents(self, irc, msg, args):
        """Look up book events going on in your area with a zip code.

        Optionally you can change the radius you want to look in by 
        passing an additional miles option.
        """
        if len(args) == 0:
            irc.reply("hai, can i have zip code 2?")
            return 
        zip = args[0]
        radius = 5
        if len(args) == 2:
            radius = args[1]

        url = "http://www.librarything.com/rss/events/location/%s&distance=%s&units=miles"
        feed = feedparser.parse(urllib2.urlopen(url % (zip, radius)))
        e = []
        for entry in feed.entries:
            e.append("%s <%s>" % (strip(entry['description']), entry['link']))
        if len(e) == 0:
            irc.reply("sorry couldn't find any book events")
        else:
            irc.reply(' ; '.join(e).encode('utf-8'))

Class = LibraryThing
