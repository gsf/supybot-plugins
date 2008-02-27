###
# Copyright (c) 2003-2005, James Vega
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
import rssparser

from BeautifulSoup import BeautifulSoup

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class TrackerError(Exception):
    pass

class Sourceforge(callbacks.PluginRegexp):
    """
    Module for Sourceforge stuff. Currently contains commands to query a
    project's most recent bugs and rfes.
    """
    threaded = True
    callBefore = ['Web']
    regexps = ['sfSnarfer']

    _reopts = re.I | re.S
    _infoRe = re.compile(r'href="(?:/track[^"]+aid=(\d+)[^"]+)">\s+([^<]+)\s+</a>',
                         _reopts)
    _hrefOpts = '&set=custom&_assigned_to=0&_status=%s&_category=100' \
                '&_group=100&order=artifact_id&sort=DESC'
    _statusOpt = {'any':100, 'open':1, 'closed':2, 'deleted':3, 'pending':4}
    _optDict = {'any':'', 'open':'', 'closed':'', 'deleted':'', 'pending':''}

    _projectURL = 'http://sourceforge.net/projects/'
    _trackerURL = 'http://sourceforge.net/support/tracker.php?aid='
    def __init__(self, irc):
        self.__parent = super(Sourceforge, self)
        self.__parent.__init__(irc)

    def isCommand(self, name):
        if name in ('bug', 'rfe', 'patch'):
            return self.registryValue('enableSpecificTrackerCommands')
        else:
            return self.__parent.isCommand(name)

    def _formatResp(self, text):
        """
        Parses the Sourceforge query to return a list of tuples that
        contain the tracker information.
        """
        for item in filter(None, self._infoRe.findall(text)):
            if self.registryValue('bold'):
                yield (ircutils.bold(item[0]),
                       utils.web.htmlToText(item[1]))
            else:
                yield (item[0], utils.web.htmlToText(item[1]))

    def _getTrackerURL(self, project, Type, status):
        """
        Searches the project's Summary page to find the proper tracker link.
        """
        try:
            text = utils.web.getUrl('%s%s' % (self._projectURL, project))
        except utils.web.Error, e:
            raise callbacks.Error, str(e)
        soup = BeautifulSoup(text)
        linkRe = re.compile(r'tracker.*;atid')
        typeRe = re.compile(r'^%s$' % Type.strip(), re.I)
        trackers = soup('div', 'topnav')[0].ul('a', {'href': linkRe})
        opts = self._hrefOpts % self._statusOpt[status]
        url = 'http://sourceforge.net%%s%s' % opts
        for tracker in trackers:
            if typeRe.search(tracker.string):
                return url % utils.web.htmlToText(tracker['href'])
        else:
            raise TrackerError, 'Invalid Tracker page'

    def _getTrackerList(self, url, type):
        """
        Searches the tracker list page and returns a list of the trackers.
        """
        try:
            text = utils.web.getUrl(url)
        except utils.web.Error, e:
            raise callbacks.Error, str(e)
        if "No matches found." in text:
            return 'No %s were found.' % type
        head = '#%i: %s'
        resp = [format(head, *entry) for entry in self._formatResp(text)]
        if resp:
            if len(resp) > 10:
                resp = map(lambda s: utils.str.ellipsisify(s, 50), resp)
            return format('%L', resp)
        raise callbacks.Error, 'No %s were found.  (%s)' % \
              (type, conf.supybot.replies.possibleBug())

    _sfTitle = re.compile(r'Detail:\s*(\d+)\s*-\s*(\w.*)', re.I)
    _linkHref = re.compile(r'atid')
    def _getTrackerInfo(self, url):
        """
        Parses the specific tracker page, returning useful information.
        """
        try:
            s = utils.web.getUrl(url)
        except utils.web.Error, e:
            raise TrackerError, str(e)
        soup = BeautifulSoup(s)
        bold = self.registryValue('bold')
        resp = []
        head = ''
        sfTitle = self._sfTitle.search(soup.title.string)
        ul = soup('ul', {'id': 'breadcrumb'})[0]
        linkType = ul.first('a', {'href': self._linkHref}).string
        if sfTitle and linkType:
            linkType = utils.str.depluralize(linkType)
            (num, desc) = sfTitle.groups()
            if bold:
                head = format('%s #%i: %s',
                              ircutils.bold(linkType), num, desc)
            else:
                head = format('%s #%i: %s', linkType, num, desc)
            resp.append(head)
        else:
            return None
        table = soup.first('table')
        props = {}
        linkRe = re.compile(r'help_window')
        for td in table('td'):
            if td.b.string:
                props[td.b.string.rstrip(': ')] = td.br.next.strip('\t\n -')
            elif td('a', {'href': linkRe}):
                props[td.b.next.rstrip(': ')] = td.br.next.strip('\t\n -')
        for prop in ('Resolution', 'Date Submitted', 'Submitted By',
                     'Assigned To', 'Priority', 'Status'):
            try:
                if bold:
                    resp.append('%s: %s' % (ircutils.bold(prop), props[prop]))
                else:
                    resp.append('%s: %s' % (prop, props[prop]))
            except KeyError:
                pass
        return '; '.join(resp)

    def bug(self, irc, msg, args, id):
        """<id>

        Returns a description of the bug with id <id>.  Really, this is
        just a wrapper for the tracker command; it won't even complain if the
        <id> you give isn't a bug.
        """
        self._tracker(irc, id)
    bug = wrap(bug, [('id', 'bug')])

    def patch(self, irc, msg, args, id):
        """<id>

        Returns a description of the patch with id <id>.  Really, this is
        just a wrapper for the tracker command; it won't even complain if the
        <id> you give isn't a patch.
        """
        self._tracker(irc, id)
    patch = wrap(patch, [('id', 'patch')])

    def rfe(self, irc, msg, args, id):
        """<id>

        Returns a description of the rfe with id <id>.  Really, this is
        just a wrapper for the tracker command; it won't even complain if the
        <id> you give isn't an rfe.
        """
        self._tracker(irc, id)
    rfe = wrap(rfe, [('id', 'rfe')])

    def tracker(self, irc, msg, args, id):
        """<id>

        Returns a description of the tracker with id <id> and the corresponding
        url.
        """
        self._tracker(irc, id)
    tracker = wrap(tracker, [('id', 'tracker')])

    def _tracker(self, irc, id):
        try:
            url = '%s%s' % (self._trackerURL, id)
            resp = self._getTrackerInfo(url)
            if resp is None:
                irc.error('Invalid Tracker page snarfed: %s' % url)
            else:
                irc.reply('%s <%s>' % (resp, url))
        except TrackerError, e:
            irc.error(str(e))

    def _trackers(self, irc, args, msg, optlist, project, tracker):
        status = 'open'
        for (option, _) in optlist:
            if option in self._statusOpt:
                status = option
        try:
            int(project)
            s = 'Use the tracker command to get information about specific '\
                '%s.' % tracker
            irc.error(s)
            return
        except ValueError:
            pass
        if not project:
            project = self.registryValue('defaultProject', msg.args[0])
            if not project:
                raise callbacks.ArgumentError
        try:
            url = self._getTrackerURL(project, tracker, status)
        except TrackerError, e:
            irc.error('%s.  I can\'t find the %s link.' %
                      (e, tracker.capitalize()))
            return
        irc.reply(self._getTrackerList(url, tracker))

    def bugs(self, irc, msg, args, optlist, project):
        """[--{any,open,closed,deleted,pending}] [<project>]

        Returns a list of the most recent bugs filed against <project>.
        <project> is not needed if there is a default project set.  Search
        defaults to open bugs.
        """
        self._trackers(irc, args, msg, optlist, project, 'bugs')
    bugs = wrap(bugs, [getopts(_optDict), additional('something', '')])

    def rfes(self, irc, msg, args, optlist, project):
        """[--{any,open,closed,deleted,pending}] [<project>]

        Returns a list of the most recent rfes filed against <project>.
        <project> is not needed if there is a default project set.  Search
        defaults to open rfes.
        """
        self._trackers(irc, args, msg, optlist, project, 'rfe')
    rfes = wrap(rfes, [getopts(_optDict), additional('something', '')])

    def patches(self, irc, msg, args, optlist, project):
        """[--{any,open,closed,deleted,pending}] [<project>]

        Returns a list of the most recent patches filed against <project>.
        <project> is not needed if there is a default project set.  Search
        defaults to open patches.
        """
        self._trackers(irc, args, msg, optlist, project, 'patches')
    patches = wrap(patches, [getopts(_optDict), additional('something', '')])

    _intRe = re.compile(r'(\d+)')
    _percentRe = re.compile(r'([\d.]+%)')
    def stats(self, irc, msg, args, project):
        """[<project>]

        Returns the current statistics for <project>.  <project> is not needed
        if there is a default project set.
        """
        url = 'http://sourceforge.net/' \
              'export/rss2_projsummary.php?project=' + project
        results = rssparser.parse(url)
        if not results['items']:
            irc.errorInvalid('SourceForge project name', project)
        class x:
            pass
        def get(r, s):
            m = r.search(s)
            if m is not None:
                return m.group(0)
            else:
                irc.error('Sourceforge gave me a bad RSS feed.', Raise=True)
        def gets(r, s):
            L = []
            for m in r.finditer(s):
                L.append(m.group(1))
            return L
        def afterColon(s):
            return s.split(': ', 1)[-1]
        try:
            for item in results['items']:
                title = item['title']
                description = item['description']
                if 'Project name' in title:
                    x.project = afterColon(title)
                elif 'Developers on project' in title:
                    x.devs = get(self._intRe, title)
                elif 'Activity percentile' in title:
                    x.activity = get(self._percentRe, title)
                    x.ranking = get(self._intRe, afterColon(description))
                elif 'Downloadable files' in title:
                    x.downloads = get(self._intRe, title)
                    x.downloadsToday = afterColon(description)
                elif 'Tracker: Bugs' in title:
                    (x.bugsOpen, x.bugsTotal) = gets(self._intRe, title)
                elif 'Tracker: Patches' in title:
                    (x.patchesOpen, x.patchesTotal) = gets(self._intRe, title)
                elif 'Tracker: Feature' in title:
                    (x.rfesOpen, x.rfesTotal) = gets(self._intRe, title)
        except AttributeError:
            irc.error('Unable to parse stats RSS.', Raise=True)
        irc.reply(
            format('%s has %n, '
                   'is %s active (ranked %i), '
                   'has had %n (%s today), '
                   'has %n (out of %i), '
                   'has %n (out of %i), '
                   'and has %n (out of %i).',
                   x.project, (int(x.devs), 'developer'),
                   x.activity, x.ranking,
                   (int(x.downloads), 'download'), x.downloadsToday,
                   (int(x.bugsOpen), 'open', 'bug'), x.bugsTotal,
                   (int(x.rfesOpen), 'open', 'rfe'), x.rfesTotal,
                   (int(x.patchesOpen), 'open', 'patch'), x.patchesTotal))
    stats = wrap(stats, ['lowered'])

    _totbugs = re.compile(r'Bugs</a>\s+?\( <b>([^<]+)</b>', re.S | re.I)
    def _getNumBugs(self, project):
        try:
            text = utils.web.getUrl('%s%s' % (self._projectURL, project))
        except utils.web.Error, e:
            raise callbacks.Error, str(e)
        m = self._totbugs.search(text)
        if m:
            return m.group(1)
        else:
            return ''

    _totrfes = re.compile(r'Feature Requests</a>\s+?\( <b>([^<]+)</b>',
                          re.S | re.I)
    def _getNumRfes(self, project):
        try:
            text = utils.web.getUrl('%s%s' % (self._projectURL, project))
        except utils.web.Error, e:
            raise callbacks.Error, str(e)
        m = self._totrfes.search(text)
        if m:
            return m.group(1)
        else:
            return ''

    def total(self, irc, msg, args, type, project):
        """{bugs,rfes} [<project>]

        Returns the total count of open bugs or rfes.  <project> is only
        necessary if a default project is not set.
        """
        if type == 'bugs':
            self._totalbugs(irc, msg, project)
        elif type == 'rfes':
            self._totalrfes(irc, msg, project)
    total = wrap(total, [('literal',('bugs', 'rfes')),additional('something')])

    def _totalbugs(self, irc, msg, project):
        project = project or self.registryValue('defaultProject', msg.args[0])
        total = self._getNumBugs(project)
        if total:
            irc.reply(total)
        else:
            irc.error('Could not find bug statistics for %s.' % project)

    def _totalrfes(self, irc, msg, project):
        project = project or self.registryValue('defaultProject', msg.args[0])
        total = self._getNumRfes(project)
        if total:
            irc.reply(total)
        else:
            irc.error('Could not find RFE statistics for %s.' % project)

    def fight(self, irc, msg, args, optlist, projects):
        """[--{bugs,rfes}] [--{open,closed}] <project name> <project name> \
        [<project name> ...]

        Returns the projects, in order, from greatest number of bugs to least.
        Defaults to bugs and open.
        """
        search = self._getNumBugs
        type = 0
        for (option, _) in optlist:
            if option == 'bugs':
                search = self._getNumBugs
            if option == 'rfes':
                search = self._getNumRfes
            if option == 'open':
                type = 0
            if option == 'closed':
                type = 1
        results = []
        for proj in projects:
            num = search(proj)
            if num:
                results.append((int(num.split('/')[type].split()[0]), proj))
        results.sort()
        results.reverse()
        s = ', '.join([format('\'%s\': %i', s, i) for (i, s) in results])
        irc.reply(s)
    fight = wrap(fight, [getopts({'bugs':'','rfes':'','open':'','closed':''}),
                         many('something')])

    def sfSnarfer(self, irc, msg, match):
        r"https?://(?:www\.)?(?:sourceforge|sf)\.net/tracker/" \
        r".*\?(?:&?func=detail|&?aid=\d+|&?group_id=\d+|&?atid=\d+){4}"
        if not self.registryValue('trackerSnarfer', msg.args[0]):
            return
        try:
            url = match.group(0)
            resp = self._getTrackerInfo(url)
            if resp is None:
                self.log.info('Invalid Tracker page snarfed: %s', url)
            else:
                irc.reply(resp, prefixNick=False)
        except TrackerError, e:
            self.log.info(str(e))
    sfSnarfer = urlSnarfer(sfSnarfer)


Class = Sourceforge


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
