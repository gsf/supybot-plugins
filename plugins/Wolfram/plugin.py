from supybot.commands import *
import supybot.callbacks as callbacks

import urllib
from xml.etree import ElementTree

app_id = '62VUEW-H6XTUTU32R'

class Wolfram(callbacks.Privmsg):

    def alpha(self, irc, msg, args):
        """Ask Mr. Wolfram a question, get an "answer"
        """
        a = ' '.join(args)
        u = "http://api.wolframalpha.com/v2/query?"
        q = urllib.urlencode(dict(input=a, appid=app_id))
        xml = urllib.urlopen(u + q).read()
        tree = ElementTree.fromstring(xml)

        answer = None
        for pod in tree.findall('.//pod'):
            title = pod.attrib['title']
            if title != 'Result':
                continue
            answer = pod.find('.//plaintext')
            if answer:
                answer = answer.text

        if answer:
            irc.reply(answer.encode("utf-8"))
        else:
            irc.reply("huh, I dunno, sorry!")


Class = Wolfram
