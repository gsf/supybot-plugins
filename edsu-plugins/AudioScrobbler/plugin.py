# -*- coding: utf-8 -*-

from os.path import join 
from urllib import quote
from urllib2 import urlopen
from random import choice
from xml.etree import ElementTree as ET
import feedparser
import simplejson
import socket
import time

from supybot.commands import *
import supybot.conf as conf
import supybot.dbi as dbi
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class AudioScrobbler(callbacks.Plugin):
    threaded = True
    class DB(plugins.DbiChannelDB):
        class DB(dbi.DB):
            class Record(dbi.Record):
                __fields__ = [
                    'at',
                    'by',
                    'nick',
                    'username',
                ]
                def get_name(self):
                    if self.nick == self.username:
                        return self.nick
                    return '%s (%s)' % (self.nick, self.username)
                name = property(get_name)
            def add(self, at, by, nick, username, **kwargs):
                record = self.Record(at=at, by=by, nick=nick, username=username, **kwargs)
                return super(self.__class__, self).add(record)
            def all_records(self):
                return self.select(lambda r: True)
            def pick(self, **kwargs):
                def p(r):
                    flag = True
                    for k in kwargs:
                        if getattr(r, k) != kwargs[k]:
                            flag = False
                    return flag
                try:
                    record = self.select(p).next()
                except StopIteration:
                    record = None
                return record
            def username(self, nick):
                record = self.pick(nick=nick)
                if record:
                    return record.username

    def __init__(self, irc):
        self.__parent = super(AudioScrobbler, self)
        self.__parent.__init__(irc)
        self.db = plugins.DB(self.name(), {'flat': self.DB})()
        #self.nickmap = dict(
        #  # last.fm username = 'IRC nick',
        #    leftwing = 'mjgiarlo',
        #    DataGazetteer = 'pmurray',
        #    LTjake = 'bricas',
        #    moil = 'gsf',
        #    rtennant = 'royt',
        #    inkdroid = 'edsu',
        #    inkcow = 'rsinger',
        #    roblivian = 'robcaSSon',
        #    mdxi = 'sboyette',
        #    bsadler = 'bess',
        #    jaydatema = 'jdatema',
        #    jfrumkin = 'jaf',
        #    ryanwick = 'wickr',
        #    ranginui = 'rangi',
        #    mangrue = 'jtgorman',
        #    dys = 'MrDys',
        #    bosteen = 'BenO',
        #    tomkeys = 'madtom',
        #)

    def _get_songs(self, username):
        socket.setdefaulttimeout(60)
        url = 'http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.rss'
        rss = feedparser.parse(url % username)
        songs = []
        for entry in rss.entries:
            song = entry.title.replace(u" – ", u' : ')
            songs.append(song.encode('utf8', 'ignore'))
        return songs

    def randtune(self, irc, msg, args, channel):
        """
        Return a random song from the neighborhood
        """
        record = self.db.random(channel)
        songs = self._get_songs(record.username)
        if len(songs) > 0:
            irc.reply(songs[0])
        else:
            irc.reply("%s is screwing up the system" % record.name)
    randtune = wrap(randtune, ['channeldb'])

    def tunes(self, irc, msg, args, channel, username):
        """[<username>]
        See what <username> (or you) last played
        """
        username = username or self.db.username(channel, msg.nick)
        if not username:
            irc.reply("No %s in the neighborhood" % nick)
            return
        songs = self._get_songs(username)
        if len(songs) > 0:
            irc.reply(songs[0])
        else:
            irc.reply("I dunno what %s last listened to" % username)
    tunes = wrap(tunes, ['channeldb', optional('text')])

    def alltunes(self, irc, msg, args, channel, username):
        """[<username>]
        See the full list of tunes <username> (or you) have played recently
        """
        username = username or self.db.username(channel, msg.nick)
        if not username:
            irc.reply("No %s in the neighborhood" % nick)
            return
        songs = self._get_songs(username)
        if len(songs) > 0:
            irc.reply(' || '.join(self._get_songs(username)))
        else:
            irc.reply('I dunno any songs %s has listened to' % username)
    alltunes = wrap(alltunes, ['channeldb', optional('text')])

    def blockparty(self, irc, msg, args, channel, show_all):
        """[all]
        See what people on the street are listening to. Include "all" to show everybody.
        """
        show_all = bool(show_all or not irc.isChannel(channel))

        irc.reply('Everybody on the block announce:', prefixNick=False)
        records = self.db.all_records(channel)
        for record in records:
            if show_all or record.nick in irc.state.channels[channel].users:
                songs = self._get_songs(record.username)
                if len(songs) > 0:
                    irc.reply('%s: %s' % (record.name, songs[0]), prefixNick=False)
    blockparty = wrap(blockparty, ['channeldb', optional('boolean')])

    def _add(self, irc, msg, args, channel, nick, username):
        """<nick> <username>
        Add somebody to the lastfm blockparty. 
        """
        record = self.db.pick(channel, nick=nick)
        if record:
            self.db.remove(channel, record.id)
        self.db.add(channel, time.time(), msg.nick, nick, username)
        record = self.db.pick(channel, nick=nick)
        irc.reply('%s just moved in across the street' % record.name, 
                prefixNick=False)
    add = wrap(_add, ['channeldb', 'nick', 'text'])

    def movein(self, irc, msg, args, channel, username):
        """[<username>]
        Move into the neighborhood. Your nick is used as the lastfm <username> if you don't specify one.
        """
        username = username or msg.nick
        self._add(irc, msg, args, channel, msg.nick, username)
    movein = wrap(movein, ['channeldb', optional('nick')])

    def get_nick_info(self, irc, msg, args, channel, nick):
        """[<nick>]
        Get when <nick> moved in. Your own nick is the default.
        """
        nick = nick or msg.nick
        record = self.db.pick(channel, nick=nick)
        if record:
            irc.reply(format('%s moved in at %t (added by %s)', 
                record.name, record.at, record.by))
        else:
            irc.reply("No %s in the neighborhood" % nick)
    get_nick_info = wrap(get_nick_info, ['channeldb', optional('nick')])

    def _remove(self, irc, msg, args, channel, nick):
        """<nick>
        Move <nick> out of the neighborhood.
        """
        record = self.db.pick(channel, nick=nick)
        if record:
            self.db.remove(channel, record.id)
            irc.reply("%s just got evicted" % nick)
        else:
            irc.reply("%s doesn't live here anymore" % nick)
    remove = wrap(_remove, ['channeldb', 'nick'])

    def moveout(self, irc, msg, args, channel):
        """
        Move yourself out of the neighborhood.
        """
        self._remove(irc, msg, args, channel, msg.nick)
    moveout = wrap(moveout, ['channeldb'])

    def _favs(self, username):
        url = "http://ws.audioscrobbler.com/1.0/user/%s/topartists.txt" % username
        try:
            response = urlopen(url)
        except:
            self.log.warning("Error in fetching %s" % url)
            return
        favs = []
        for row in urlopen(url):
            favs.append(row.split(',')[2].strip("\n"))
            if len(favs) >= 20:
                break
        return favs

    def favs(self, irc, msg, args, channel, username):
        """[<username>]
        Get <username>'s (or your own) favorite artists
        """
        username = username or self.db.username(channel, msg.nick)
        if not username:
            irc.reply("No %s in the neighborhood" % nick)
            return
        favs = self._favs(username)
        if favs:
            irc.reply(', '.join(favs).encode('utf8', 'ignore'))
        else:
            irc.reply('no such user "%s" or last.fm is on the fritz' % username)
    favs = wrap(favs, ['channeldb', optional('nick')])

    def taste(self, irc, msg, args, channel, username):
        """[<username>]
        Get the top tags of <username>'s fav artists (or your own)
        """
        username = username or self.db.username(channel, msg.nick)
        if not username:
            irc.reply("No %s in the neighborhood" % nick)
            return
        try:
            favs = self._favs(username)
        except:
            irc.reply('no such user "%s" or last.fm is on the fritz' % username)
        fav_tags = {}
        for fav in favs:
            tags = self._tags(fav)
            if tags:
                for tag in tags:
                    tag = tag.split(':')[0]
                    fav_tags.setdefault(tag, 0)
                    fav_tags[tag] += 1
            else:
                irc.reply("No tags found for %s" % fav)
                #self.log.info("No tags found for %s" % fav)
        sorted_fav_tags = sorted(fav_tags, key=fav_tags.get, reverse=True)[:20]
        tastes = ["%s: %s" % (w, fav_tags[w]) for w in sorted_fav_tags]
        irc.reply(', '.join(tastes).encode('utf8', 'ignore'))
    taste = wrap(taste, ['channeldb', optional('nick')])

    def scrobblers(self, irc, msg, args, channel):
        """
        Show everybody on the block
        """
        records = self.db.all_records(channel)
        users = "; ".join(record.name for record in records)
        if users:
            irc.reply(users)
        else:
            irc.reply('you have one quiet block')
    scrobblers = wrap(scrobblers, ['channeldb'])

    def recommend(self, irc, msg, args, channel, artist):
        """<artist>
        Get recommendations for an artist
        """
        if artist.lower() == 'lightning bolt':
            irc.reply("I recommend you listen to something else...")
            return
        if artist.lower() == 'motley crue':
            irc.reply("No")
            return
        url = 'http://ws.audioscrobbler.com/1.0/artist/%s/similar.xml' % quote(artist)
        root = self._get_root(url)
        if not root:
            irc.reply("Can't get no recommendations for \"%s\"" % artist)
            return
        names = []
        for name in root.findall('.//name'):
            names.append(name.text)
        irc.reply(', '.join(names).encode('utf8','ignore'))
    recommend = wrap(recommend, ['channeldb', 'text'])

    def weeklies(self, irc, msg, args, channel, username):
        """[<username>]
        Get a weekly top 10 for a last.fm username (or yourself)
        """
        username = username or self.db.username(channel, msg.nick)
        if not username:
            irc.reply("No %s in the neighborhood" % nick)
            return
        url = 'http://ws.audioscrobbler.com/1.0/user/%s/weeklytrackchart.xml' % username
        root = self._get_root(url)
        if not root:
            irc.reply("Weeklies is wrecked")
            return
        tracks = []
        for track in root.findall('.//track'):
            artist = track.find('.//artist').text
            title = track.find('.//name').text
            count = track.find('.//playcount').text
            tracks.append("%s - %s [%s]" % (artist, title, count))
        irc.reply('; '.join(tracks).encode('utf8','ignore'))
    weeklies = wrap(weeklies, ['channeldb', optional('nick')])

    def tags(self, irc, msg, args, channel, artist):
        """<artist>
        Get tags for an artist
        """
        tags = self._tags(artist)
        if tags:
            irc.reply(' ; '.join(tags).encode('utf8','ignore'))
        else:
            irc.reply("No tags could be gotten")
    tags = wrap(tags, ['channeldb', 'text'])

    def _tags(self, artist):
        url = "http://ws.audioscrobbler.com/1.0/artist/%s/toptags.xml" % quote(artist)
        root = self._get_root(url)
        if not root:
            return
        tags = []
        for tag in root.findall('.//tag'):
            name = tag.find(".//name")
            count = tag.find(".//count")
            tags.append("%s: %s%%" % (name.text, count.text))
        return tags

    def toptracks(self, irc, msg, args, channel):
        """
        Get the last.fm weekly track chart
        """
        url = 'http://ws.audioscrobbler.com/1.0/group/code4lib/weeklytrackchart.xml'
        root = self._get_root(url)
        if not root:
            irc.reply('last.fm is on the fritz or something')
            return
        tracks = []
        for track in root.findall('.//track'):
            artist = track.find('.//artist')
            name = track.find('.//name')
            tracks.append("%s:%s" % (artist.text.strip(), name.text.strip()))
        irc.reply(', '.join(tracks).encode('utf8','ignore'))
    toptracks = wrap(toptracks, ['channeldb'])

    def _get_root(self, url):
        try:
            response = urlopen(url)
        except:
            self.log.warning("Error in fetching %s" % url)
            return
        tree = ET.parse(response)
        return tree.getroot()

    def _topbands(self, irc, msg, args, channel, random):
        """[random]
        Get the last.fm weekly band chart. Include "random" to choose a random one.
        """
        url = 'http://ws.audioscrobbler.com/1.0/group/code4lib/weeklyartistchart.xml'
        root = self._get_root(url)
        if not root:
            irc.reply('last.fm is on the fritz or something')
            return
        artists = []
        for track in root.findall('.//artist'):
            name = track.find('.//name')
            artists.append(name.text.strip())
        if random:
            artist = choice(artists)
            irc.reply(artist)
        irc.reply(', '.join(artists).encode('utf8','ignore'))
    topbands = wrap(_topbands, ['channeldb', optional('boolean')])

    def randband(self, irc, msg, args, channel):
        """
        Returns a random band from the weekly top 
        artists chart of the code4lib last.fm group
        """
        self._topbands(irc, msg, args, channel, True)
    randband = wrap(randband, ['channeldb'])

    def tagged(self, irc, msg, args, channel, tag):
        """<tag>
        Get all bands tagged with <tag>
        """
        url = "http://ws.audioscrobbler.com/1.0/tag/%s/topartists.xml" % quote(tag.strip())
        root = self._get_root(url)
        if not root:
            irc.reply('no tag "%s" or last.fm is on the fritz' % tag)
            return
        tags = []
        for artist in root.findall('.//artist'):
            tags.append("%s: %s%%" % (artist.attrib['name'],
                int(float(artist.attrib['count']))))
        irc.reply(' ; '.join(tags).encode('utf8','ignore'))
    tagged = wrap(tagged, ['channeldb', 'text'])

    def commontags(self, irc, msg, args, channel, artists):
        """<artist> <artist> [<artist>] ...
        Get common tags among a bunch of artists
        """
        artists = artists.split(':')
        tags = {}
        for artist in artists:
            url = "http://ws.audioscrobbler.com/1.0/artist/%s/toptags.xml" % quote(artist.strip())
            root = self._get_root(url)
            if not root:
                irc.reply('no artist "%s" or last.fm is on the fritz' % artist)
                return
            for tag in root.findall('.//tag'):
                name = tag.find(".//name").text
                if tags.has_key(name):
                    tags[name] += 1
                else:
                    tags[name] = 1
        common_tags = []
        for tag in tags:
            if tags[tag] == len(artists):
                common_tags.append(tag)
        irc.reply(' ; '.join(common_tags).encode('utf8','ignore'))
    commontags = wrap(commontags, ['channeldb', 'text'])

Class = AudioScrobbler 
