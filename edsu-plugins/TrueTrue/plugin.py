import supybot.callbacks as callbacks
from random import randint
import time

class TrueTrue(callbacks.PluginRegexp):
    regexps = ['cassonSnarfer', 'chuckleSnarfer', 'upchuckSnarfer', 
               'coughSnarfer', 'metadataSnarfer', 'crueSnarfer', 'knockSnarfer',
               'panizziSnarfer', 'opacSnarfer', 'yawnSnarfer', 'callMeSomething',
               'snortSnarfer', 'sobSnarfer', 'hollaBackSnarfer',
               'hornsSnarfer',
               # 'youRangSnarfer', 'billSnarfer', 'hehSnarfer'
               ] 

    def hornsSnarfer(self, irc, msg, match):
        r"\\m/"
        time.sleep(2)
        irc.reply("bangs its head!", action=True, prefixNick=False)

    def hollaBackSnarfer(self,irc,msg,match):
        r"^zoia([!.?]+)$"
        irc.reply('%s%s' % (msg.nick,match.group(1)), prefixNick=False)

# Redundant now
#    def youRangSnarfer(self,irc,msg,match):
#        r"^zoia\?$"
#        irc.reply('%s?' % (msg.nick), prefixNick=False)
        
    def cassonSnarfer(self,irc,msg,match):
        r"true, true"
        time.sleep(2)
        if msg.nick == 'robcaSSon':
            irc.reply("tsk tsk")
        else:
            irc.reply("chuckles", action=True, prefixNick=False)
            
    def crueSnarfer(self,irc,msg,match):
        r"crue"
        irc.reply("turn it up!")

    def opacSnarfer(self,irc,msg,match):
        r" opac "
        if randint(1,10) != 1: return
        irc.reply("here we go again ...", prefixNick=False)

    def metadataSnarfer(self,irc,msg,match):
        r"metadata"
        # lets not be totally predictable
        if randint(1,10) != 1: return
        time.sleep(10)
        responses = [
            'can you tell me more about this metadata stuff?',
            'i think there is a xslt crosswalk for that',
            'is that like data about data?',
            "Don't cry for me, Metadataaaaa!",
            "i never met a data i did not like too",
            'can i get a witness?',
            'Greeks prefer fetadata',
            'its just data, jeez',
            'take my metadata, please?',
            'metadata is for the birds, tweet, tweet, tweet',
            'can we talk about something else?'
            'is metadata like xml and stuff?',
            'infinite recursion error',
            "And don't get me started about metadata!",
            "You say metadata \ I say data about data \ let's call the whole thing off",
            'and on the 8th day god made metadata...and it was good',
            'Can you shut the hell up for one minute about the metadata?',
            'Metadata, metadata, metadata!  What about MARC?',
            'marc is dead, long live ummm...metadata']
        irc.reply(responses[randint(0,len(responses))], prefixNick=False)

    def chuckleSnarfer(self,irc,msg,match):
        r"chuckles"
        time.sleep(2)
        if randint(1,5) != 1: return
        irc.reply("true, true", prefixNick=False)

    def coughSnarfer(self,irc,msg,match):
        r"coughs"
        time.sleep(2)
        irc.reply("sneezes", action=True, prefixNick=False)
        
    def upchuckSnarfer(self,irc,msg,match):
        r"upchucks"
        time.sleep(2)
        if randint(0,1) == 0:
            who = 'robcaSSon'
        else:
            nicks = list(irc.state.channels[msg.args[0]].users)
            who = nicks[randint(0,len(nicks)-1)]
        aisle = randint(1,10)
        irc.reply(("%s: clean up on aisle %i" % (who, aisle)), prefixNick=False)

    def yawnSnarfer(self,irc,msg,match):
        r"yawns"
        time.sleep(2)
        irc.reply("WAKE UP!")

    def knockSnarfer(self,irc,msg,match):
        r"knock knock"
        time.sleep(2)
        irc.reply("Who's there?")

#   commented out on request
#    def billSnarfer(self,irc,msg,match):
#        r"bdrew|bill drew|Bill Drew|Bill Gates|bgates|bill gates"
#        time.sleep(2)
#        irc.reply("thanks, bill!", prefixNick=False)

    def panizziSnarfer(self, irc, msg, match):
        r'panizzi|Panizzi'
        if randint(1,5) != 1: return
        time.sleep(2)
        irc.reply("panizzi is dead. long live panizzi!", prefixNick=False)

    def hehSnarfer(self, irc, msg, match):
    	r'^heh$'
    	time.sleep(2)
    	if randint(1,10) == 1: 
            irc.reply("it wasn't that funny...")
    	else:
            irc.reply("typical...", prefixNick=False)

    def callMeSomething(self, irc, msg, match):
        r'^[Cc]all me (.+?)(?:[.;:]|(?:,?\s*\b(and|if|but)\b)|$)'
        time.sleep(2)
        irc.reply("You're %s." % (match.group(1)))
      
    def sobSnarfer(self, irc, msg, match):
        r'\bsobs\b'
        if randint(1,5) > 2: return
        time.sleep(2)
        irc.reply('snorts', action=True, prefixNick=False)

    def snortSnarfer(self, irc, msg, match):
        r'\bsnorts\b' 
        if randint(1,5) > 2: return
        time.sleep(2)
        irc.reply('sobs', action=True, prefixNick=False)

            
Class = TrueTrue
