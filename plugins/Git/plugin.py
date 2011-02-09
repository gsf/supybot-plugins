###
# Copyright (c) 2010, Michael B. Klein
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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re
import simplejson
import supybot.utils.web as web

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; Github Plugin; http://code4lib.org/irc)')

class Git(callbacks.Plugin):
    """Git/Github-related commands"""

    def _fetch_json(self, url):
        doc = web.getUrl(url, headers=HEADERS)
        try:
            json = simplejson.loads(doc)
        except ValueError:
            return None
        return json

    def commits(self, irc, msg, args, opts, query):
      """[--author author] [--repo repo] [--branch branch] [--show number] [query]
      
      Display the last <number> log messages matching <query> from <author>'s commits to <branch> of <repo> on github"""
      repo = 'gsf/supybot-plugins'
      branch = 'master'
      author = ''
      path = None
      commits = 1
      for (opt, arg) in opts:
          if opt == 'repo':
            repo = arg
          if opt == 'branch':
            branch = arg
          if opt == 'path':
            path = arg
          if opt == 'show':
            commits = arg
          if opt == 'author':
            author = arg
      
      if path is None:
        branch_path = branch
      else:
        branch_path = '%s/%s' % (branch,path)
      data = self._fetch_json('http://github.com/api/v2/json/commits/list/%s/%s?author=%s' % (repo,branch_path,author))

      if query is None:
        matching_commits = data['commits']
      else:
        pattern = re.compile(query)
        matching_commits = filter(lambda c: pattern.search(c['message']),data['commits'])
      
      found = min(commits,len(matching_commits))
      if found == 0:
        irc.reply('No matching commits found in %s:%s' % (repo, branch))
      else:
        for i in range(found):
          commit = matching_commits[i]
          (date, time) = commit['committed_date'][0:19].split('T')
          commit.update({ 'display_date' : date, 'display_time' : time, 'display_committer' : commit['committer']['login'] })
          commit['message'] = commit['message'].split('git-svn-id')[0].strip()
          log_line = "[%(display_date)10.10s %(display_time)8.8s] [%(display_committer)s] %(message)s" % commit
          log_line = re.sub(r'\n',' ',log_line)
          irc.reply(log_line, prefixNick=False)
    commits = wrap(commits, [getopts({'repo':'somethingWithoutSpaces',
      'branch':'somethingWithoutSpaces','path':'somethingWithoutSpaces',
      'show':'int','author':'somethingWithoutSpaces'}),optional('text')])

    def repo(self, irc, msg, args, opts, query):
      irc.reply('https://github.com/gsf/supybot-plugins', prefixNick=True)
      
Class = Git


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
