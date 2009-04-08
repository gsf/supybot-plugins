from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from xml.etree import ElementTree as ET
from os.path import dirname, abspath
from random import randint

marcdoc = ET.parse("%s/%s" % (dirname(abspath(__file__)), 'marcdoc.xml'))

def field_desc(tag):
  for f in marcdoc.findall('field'):
    if f.attrib['tag'] == tag:
      desc = f.findtext('description')
      repeatable = "(Repeatable) " if f.attrib['repeatable'] == "true" else ""        
      subfields = [sf.attrib['code'] for sf in f.findall('subfield')]
      return "%s %s[%s]" % (desc, repeatable, ','.join(subfields))
  return "unknown tag %s" % tag

def subfield_desc(tag, code):
  for f in marcdoc.findall('field'):
    if f.attrib['tag'] == tag:
      for sf in f.findall('subfield'):
        if sf.attrib['code'] == code:
          repeatable = " (Repeatable) " if f.attrib['repeatable'] == "true" else ""
          return "%s%s" % (sf.findtext('description'), repeatable)
  return "unknown field/subfield combination (%s/%s)" % (tag, code)

class MARC(callbacks.Privmsg):

  def marc(self,irc,msg,args):
    """look up field or field/subfield combo in MARC docs

    eg. @marc 245  or  @marc 245 a
    """
    if len(args) == 0:
      irc.reply('must supply at least a field to look up')
      return

    field = args.pop(0)
    subfield = None
    if len(args) > 0: subfield = args.pop(0)

    if subfield:
      irc.reply(subfield_desc(field, subfield))
    else:
      irc.reply(field_desc(field))

  def rand(self, irc, msg, args):
    tags = [f.attrib['tag'] for f in  marcdoc.findall('field')]
    tag = tags[randint(0, len(tags))]
    irc.reply("%s: %s" % (tag, field_desc(tag)))
    
    
Class = MARC 

