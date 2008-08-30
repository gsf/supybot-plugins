# -*- coding: utf-8 -*-
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener
from random import randint

class Presidents(callbacks.Privmsg):
    def mccain(self, irc, msg, args):
        """grabs a line from http://www.johnmccainisyourjalopy.com/
        """
        url = 'http://www.johnmccainisyourjalopy.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('a').string.strip().upper())

    def ronpaul(self, irc, msg, args):
        """grabs a line from http://ronpaulisyournewbicycle.com/
        """
        url = 'http://ronpaulisyournewbicycle.com/'
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        html = opener.open(url)
        html_str = html.read()
        soup = BeautifulSoup(html_str)
        irc.reply(soup.find('a').string.strip().upper())

    def sarahpalin(self, irc, msg, args):
        """Taken from http://www.dailykos.com/storyonly/2008/8/29/14238/1838"""
        choices = u"""Sarah Palin is your new Segway.
        Sarah Palin is your New New Coke.
        Sarah Palin is your new FoxTrax.
        Sarah Palin is your new Edsel.
        Sarah Palin is your new Dennis Miller on Monday Night Football.
        Sarah Palin is your new Nü Metal.
        Sarah Palin is your new Betamax.
        Sarah Palin is your new Dunder Mifflin Infinity.
        Sarah Palin is your new Windows Vista.
        Sarah Palin is your new OK Cola.
        Sarah Palin is your new Stone Temple Pilots reunion tour.
        Sarah Palin is your new Emily's Reasons Why Not.
        Sarah Palin is your new Ryan Leaf.
        Sarah Palin is your new Star Wars Episodes I-III, plus the Clone Wars.
        Sarah Palin is your new Ford Pinto.
        Sarah Palin is your new Cuil.
        Sarah Palin is your new Dick Sargent.
        Sarah Palin is your new XFL.
        Sarah Palin is your new Apple Newton.
        Sarah Palin is your new Brett Favre's retirement.
        Sarah Palin is your new Laserdisc.
        Sarah Palin is your new Olestra.
        Sarah Palin is your new fill in the blank game in comments.""".split("\n")
        irc.reply(choices[randint(0, len(choices) - 1)].strip())

Class = Presidents

