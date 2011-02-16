from supybot.commands import *
import supybot.callbacks as callbacks

import urllib
from xml.etree import ElementTree

app_id = '62VUEW-H6XTUTU32R'

class Wolfram(callbacks.Privmsg):

    def alpha(self, irc, msg, args, question):
        """Ask Mr. Wolfram a question, get an "answer"...maybe? It uses the
        Wolfram Alpha API.
        <http://products.wolframalpha.com/docs/WolframAlpha-API-Reference.pdf>
        """
        u = "http://api.wolframalpha.com/v2/query?"
        q = urllib.urlencode({'input': question, 'appid': app_id})
        xml = urllib.urlopen(u + q).read()
        tree = ElementTree.fromstring(xml)

        found = False
        for pod in tree.findall('.//pod'):
            title = pod.attrib['title']
            for plaintext in pod.findall('.//plaintext'):
                if plaintext.text:
                    found = True
                    irc.reply(("%s: %s" % (title, plaintext.text)).encode('utf-8'))
        if not found:
            irc.reply("huh, I dunno, I'm still a baby AI. Wait till the singularity I guess?")

    alpha = wrap(alpha, ['text'])


Class = Wolfram
