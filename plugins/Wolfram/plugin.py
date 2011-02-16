from supybot.commands import *
import supybot.callbacks as callbacks

import urllib
from xml.etree import ElementTree

app_id = '62VUEW-H6XTUTU32R'

class Wolfram(callbacks.Privmsg):

    def alpha(self, irc, msg, args):
        """Ask Mr. Wolfram a question, get an "answer"
        """
        a = ' '.join(sys.argv[1:])
        u = "http://api.wolframalpha.com/v2/query?"
        q = urllib.urlencode(dict(input=a, appid=app_id))
        xml = urllib.urlopen(u + q).read()
        answer = None

        tree = ElementTree.fromstring(xml)
        for pod in tree.findall('.//pod'):
            title = pod.attrib['title']
            if title != 'Result':
                continue
            answer = pod.find('.//plaintext')
            if answer:
                answer = answer.text

        if answer:
            irc.reply(answer)
        else:
            irc.reply("huh, I dunno, sorry!")


Class = Wolfram
