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

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.registry as registry
import supybot.utils.web as web
import supybot.log as log
import sys
import time
from random import randrange
import simplejson
from urllib import urlencode
from BeautifulSoup import BeautifulStoneSoup
from languages import Languages, validateLanguage

HEADERS = dict(ua = 'Zoia/1.0 (Supybot/0.83; http://code4lib.org/irc)', referer = 'http://irc.code4lib.org/')

class TranslationError(Exception):
    def __init__(self, code=None, value=None, url=None, stack=None):
        self.code = code
        self.value = value
        self.url = url
        self.stack = stack
    
    def __str__(self):
        if self.code == None:
            return self.value
        else:
            return "%d: %s" % (self.code, self.value)
        
class TranslationParty(callbacks.Plugin):
    """Add the help for "@plugin help TranslationParty" here
    This should describe *how* to use this plugin."""
    threaded = True

    def _getJsonResponse(self,url,retries = 2):
        try:
            log.debug('Retrieving: %s' % (url))
            doc = web.getUrl(url, headers=HEADERS)
            log.debug('Response: %s' % (doc))
            response = simplejson.loads(doc)
            return response
        except web.Error, e:
            log.warning('Error: %s',str(e))
            if retries > 0:
                log.warning('Retries left: %d' % (retries))
                return self._getJsonResponse(url,retries=retries-1)
                
    def _translate(self, from_lang, to_lang, text):
        q = unicode(text, 'utf8')
        q = q.encode('utf8')
        #raise Exception, q
        params = { 
            'langpair': u'|'.join((from_lang,to_lang)), 
            'q': q, 
            'v': '1.0',
        }
        url = 'http://ajax.googleapis.com/ajax/services/language/translate?' + urlencode(params)
        response = self._getJsonResponse(url)
        if response['responseStatus'] == 404:
            log.warning('Waiting 1/2 second and retrying...')
            time.sleep(0.5)
            response = self._getJsonResponse(url)
            
        if response['responseStatus'] == 200:
            translation = unicode(BeautifulStoneSoup(response['responseData']['translatedText'],convertEntities=BeautifulStoneSoup.HTML_ENTITIES)).encode('utf8')
            return translation
        else:
            raise TranslationError(response['responseStatus'], response['responseDetails'], url)
    
    def _party(self, langs, text, max_translations = 50):
        delay = self.registryValue('delay')
        stack = [{'lang': langs[0], 'text': text}]
        def iterate():
            l = list(reversed(langs))
            while len(l) > 0:
                f = l.pop()
                if len(l) == 0:
                    t = langs[0]
                else:
                    t = l[-1]
                stack.append({'lang': t, 'text': self._translate(f,t,stack[-1]['text'])})
                time.sleep(delay)
                
        def equilibrium():
            if len(stack) < (len(langs) * 2):
                return False
                
            for i in range(-1,-(len(langs)+1),-1):
                if stack[i]['text'] != stack[i-len(langs)]['text']:
                    return False
            return True
            
        try:
            iterate()
            
            while (len(stack) < max_translations) and not equilibrium():
                iterate()
            return(stack)
        except TranslationError, e:
            e.stack = stack
            raise e

    def languages(self, irc, msg, args, query):
        """[<stem>]
        List languages known to TranslationParty that begin with <stem>"""
        if query == None:
            query = ''
        else:
            query = query.upper()
            
        result = map(lambda x: x.title(), sorted(filter(lambda x: x.startswith(query), Languages)))
        irc.reply(', '.join(result).encode('utf-8'))
    languages = wrap(languages, [optional('somethingWithoutSpaces')])
    
    def translationparty(self, irc, msg, args, opts, text):
        """[--lang <language>[,...]] [--show <none|one|all>] [--max <int>] [--verbose] <text>
        Try to find equilibrium in back-and-forth translations of <text>. (Defaults: --lang ja --show none --max 50)"""
        input_langs = ['ja']
        show = 'none'
        max_translations = 50
        announce = False
        
        if len(text) > 1000:
            irc.reply('The text to be translated cannot exceed 1000 characters. Your request contains %d characters' % (len(text)))
        else:
            for (opt,arg) in opts:
                if opt == 'lang':
                    input_langs = arg.split(',')
                if opt == 'max':
                    max_translations = arg
                if opt == 'verbose':
                    announce = True
                if opt == 'show':
                    show = arg
        
            try:
                langs = ['en']
                for l in input_langs:
                    iso_code = validateLanguage(l)
                    if iso_code == None:
                        raise TranslationError(value="Unknown language: %s" % (l))
                    langs.append(iso_code)

                result = self._party(langs, text, max_translations)

                if announce:
                    if len(result) < max_translations:
                        irc.reply("Equilibrium found!")
                    else:
                        irc.reply("It is doubtful that this phrase will ever reach equilibrium.")

                texts = map(lambda x: x['text'],result)
                if show == 'all':
                    irc.reply(" -> ".join(texts).encode('utf8'))
                elif show == 'one':
                    irc.reply(" -> ".join((texts[0],texts[-1])).encode('utf8'))
                else:
                    # STILL TOO VERBOSE
                    #irc.reply(('%(text)s [%(iterations)d iterations]' % { 'iterations' : len(texts), 'text' : texts[-1] }).encode('utf8'))
                    irc.reply(('%(text)s' % texts[-1]).encode('utf8'))
            except TranslationError, e:
                irc.reply(e)
                log.error(str(e))
                if e.stack is not None:
                    texts = map(lambda x: '[%s] %s' % (x['lang'],x['text']),e.stack)
                    log.debug("Stack: %s" % (" -> ".join(texts).encode('utf8')))
                if e.url is not None:
                    log.debug("Last URL: %s" % (e.url))
            
    translationparty = wrap(translationparty, [getopts({'lang':'somethingWithoutSpaces','show':("literal", ("none","one","all")),'max':'int','verbose':''}), 'text'])
        
Class = TranslationParty


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
