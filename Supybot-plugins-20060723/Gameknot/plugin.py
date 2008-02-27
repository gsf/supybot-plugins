###
# Copyright (c) 2003-2005, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import re

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Gameknot(callbacks.PluginRegexp):
    threaded = True
    callBefore = ['Web']
    regexps = ['gameknotSnarfer', 'gameknotStatsSnarfer']
    _gkrating = re.compile(r'<font color="#FFFF33">(\d+)</font>')
    _gkgames = re.compile(r's:</td><td class=sml>(\d+)</td></tr>')
    _gkrecord = re.compile(r'"#FFFF00">(\d+)[^"]+"#FFFF00">(\d+)[^"]+'
                           r'"#FFFF00">(\d+)')
    _gkteam = re.compile(r'Team:(<.*?>)+(?P<name>.*?)</span>')
    _gkseen = re.compile(r'(seen on GK:\s+([^[]+ago)|.*?is hiding.*?)')

    def getStats(self, name):
        gkprofile = 'http://www.gameknot.com/stats.pl?%s' % name
        try:
            profile = utils.web.getUrl(gkprofile)
            rating = self._gkrating.search(profile).group(1)
            games = self._gkgames.search(profile).group(1)
            (w, l, d) = self._gkrecord.search(profile).groups()
            try:
                w = int(w)
                l = int(l)
                d = int(d)
                wp = 100. * w / (w + l + d) # win percent
                lp = 100. * l / (w + l + d) # loss percent
                dp = 100. * d / (w + l + d) # draw percent
            except (ValueError, ZeroDivisionError):
                w = w
                wp = 0.
                l = l
                lp = 0.
                d = d
                dp = 0.
            seen = self._gkseen.search(utils.web.htmlToText(profile))
            if seen is None:
                seen = ''
            elif 'is hiding' in seen.group(0):
                seen = format('%s is hiding his/her online status.', name)
            elif seen.group(2).startswith('0'):
                seen = format('%s is on gameknot right now.', name)
            else:
                seen = format('%s was last seen on Gameknot %s.',
                              name, seen.group(2))
            games = format('%n', (int(games), 'active', 'game'))
            if 'Team:' in profile:
                team = self._gkteam.search(profile).group('name')
                team = utils.web.htmlToText(team)
                s = format('%s (team: %s) is rated %i and has %s '
                           'and a record of %n, %n, and %n '
                           '(win/loss/draw percentage: '
                           '%.2f%%/%.2f%%/%.2f%%).  %s',
                           name, team, rating, games,
                           (w, 'win'), (l, 'loss'), (d, 'draw'),
                           wp, lp, dp, seen)
            else:
                s = format('%s is rated %i and has %s '
                           'and a record of %n, %n, and %n '
                           '(win/loss/draw percentage: '
                           '%.2f%%/%.2f%%/%.2f%%).  %s',
                           name, rating, games,
                           (w, 'win'), (l, 'loss'), (d, 'draw'),
                           wp, lp, dp, seen)
            return s
        except AttributeError:
            if format('User %s not found!', name.lower()) in profile:
                raise callbacks.Error, format('No user %s exists.', name)
            else:
                raise callbacks.Error, \
                      format('The format of the page was odd.  %s',
                             conf.supybot.replies.possibleBug())
        except utils.web.Error, e:
            raise callbacks.Error, utils.web.strError(e)


    def gkstats(self, irc, msg, args, name):
        """<name>

        Returns the stats Gameknot keeps on <name>.  Gameknot is an online
        website for playing chess (rather similar to correspondence chess, just
        somewhat faster) against players from all over the world.
        """
        irc.reply(self.getStats(name))
    gkstats = wrap(gkstats, ['text'])

    _gkPlayer = re.compile(r"popd\('(Rating[^']+)'\).*?>([^<]+)<")
    _gkRating = re.compile(r": (\d+)[^:]+:<br>(\d+)[^,]+, (\d+)[^,]+, (\d+)")
    _gkGameTitle = re.compile(r"<td[^>]+><p><b>(.*?)\s*</b><br>")
    _gkWon = re.compile(r'>(\S+)\s+won')
    _gkReason = re.compile(r'won\s+\(\S+\s+(\S+)\)')
    def gameknotSnarfer(self, irc, msg, match):
        r"http://(?:www\.)?gameknot\.com/chess\.pl\?bd=\d+"
        if not self.registryValue('gameSnarfer', msg.args[0]):
            return
        url = match.group(0)
        try:
            s = utils.web.getUrl(url)
        except utils.web.Error, e:
            self.log.debug('Unable to snarf Gameknot URL: %s',
                           utils.web.strError(e))
            return
        try:
            if 'no longer available' in s:
                s = 'That game is no longer available.'
                irc.reply(s, prefixNick=True)
                return
            m = self._gkGameTitle.search(s)
            if m is None:
                self.log.debug('_gkGameTitle didn\'t match %u.', url)
                return
            gameTitle = m.groups()
            gameTitle = ircutils.bold(gameTitle)
            L = self._gkPlayer.findall(s)
            if not L:
                self.log.debug('_gkPlayer didn\'t match %u.', url)
                return
            ((wRating, wName), (bRating, bName)) = L
            wName = ircutils.bold(wName)
            bName = ircutils.bold(bName)
            if 'to move...' in s:
                if 'white to move' in s:
                    toMove = wName + ' to move.'
                else:
                    toMove = bName + ' to move.'
            else:
                # Game is over.
                m = self._gkWon.search(s)
                if m:
                    winner = m.group(1)
                    m = self._gkReason.search(s)
                    if m:
                        reason = m.group(1)
                    else:
                        reason = 'lost'
                    if winner == 'white':
                        toMove = format('%s won, %s %s.', wName, bName, reason)
                    else:
                        toMove = format('%s won, %s %s.', bName, wName, reason)
                else:
                    toMove = 'The game was a draw.'
            (wRating, wWins, wLosses, wDraws) = \
                      self._gkRating.search(wRating).groups()
            (bRating, bWins, bLosses, bDraws) = \
                      self._gkRating.search(bRating).groups()
            wStats = format('%i; W-%i, L-%i, D-%i',
                            wRating, wWins, wLosses, wDraws)
            bStats = format('%i; W-%i, L-%i, D-%i',
                            bRating, bWins, bLosses, bDraws)
            s = format('%s: %s (%s) vs. %s (%s);  %s',
                       gameTitle, wName, wStats, bName, bStats, toMove)
            irc.reply(s, prefixNick=False)
        except ValueError:
            s = format('%u doesn\'t appear to be a proper Gameknot game.', url)
            self.log.debug('Unable to snarf.  %s', s)
        except Exception, e:
            self.log.warning(utils.exnToString(e))
    gameknotSnarfer = urlSnarfer(gameknotSnarfer)

    def gameknotStatsSnarfer(self, irc, msg, match):
        r"http://gameknot\.com/stats\.pl\?([^& ]+)"
        if not self.registryValue('statSnarfer', msg.args[0]):
            return
        name = match.group(1)
        s = self.getStats(name)
        irc.reply(s, prefixNick=False)
    gameknotStatsSnarfer = urlSnarfer(gameknotStatsSnarfer)


Class = Gameknot


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
