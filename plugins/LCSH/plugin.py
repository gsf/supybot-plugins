from supybot.commands import *
import supybot.callbacks as callbacks

from urllib2 import urlopen, Request
from urllib import urlencode
import simplejson

class LCSH(callbacks.Privmsg):

    def search(self, irc, msg, args):
        """lcsh search for headings
        """
        heading = ' '.join(args)
        headings = self.do_search(heading)
        results = map(lambda r: "%s <%s>" % (r['pref_label'], r['uri']), headings)
        if not results:
            irc.reply('sorry no hits for %s, email Sandy Berman' % heading)
        else:
            irc.reply('; '.join(results).encode('utf-8'))

    def lcsh(self, irc, msg, args):
        """display information for a heading
        """
        heading = ' '.join(args)
        headings = self.do_search(' '.join(args))

        found_heading = None
        for h in headings:
            if h['pref_label'] == heading:
                found_heading = h
       
        if not found_heading:
            irc.reply(("couldn't find concept for %s " + 
                "try searching with search") % heading)
            return

        url = found_heading['uri']
        json = urlopen(Request(url, None, {'Accept': 'application/json'})).read()
        concept = simplejson.loads(json)
        msg = [concept['pref_label']]

        if concept['alt_labels']:
            msg.append('see from: ' + (', '.join(concept['alt_labels'])))

        self.add_concept_list(concept, 'broader', msg)
        self.add_concept_list(concept, 'narrower', msg)
        self.add_concept_list(concept, 'related', msg)

        irc.reply(' ; '.join(msg))


    def add_concept_list(self, concept, type, msg):
        if concept[type]:
            msg.append((type + ': ' + ', '.join(
                [
                  "%s <%s>" % (h['pref_label'], h['uri']) 
                  for h in concept[type]
                ])))

    def do_search(self, heading):
        url = 'http://lcsh.info/search?' + urlencode({'q': heading})
        json = urlopen(Request(url, None, {'Accept': 'application/json'})).read()
        return simplejson.loads(json)

Class = LCSH
