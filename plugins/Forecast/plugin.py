import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import re
import urlparse

from BeautifulSoup import BeautifulSoup
from urllib2 import build_opener, HTTPError

class Forecast(callbacks.Privmsg):

    def _fetch(self, url):
      ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
      opener = build_opener()
      opener.addheaders = [('User-Agent', ua)]
      html = opener.open(url)
      html_str = html.read()
      return BeautifulSoup(html_str)
      
    def forecast(self, irc, msg, args, opts, zipcode):
        """
        <zipcode>: Returns the response from http://www.thefuckingweather.com/
        """
        site = 'http://www.thefuckingweather.com/?zipcode=%s' % zipcode
        try:
            soup = self._fetch(site)
            response = soup.find('div', 'large').findAll(text=True)
            response = u' '.join([x.strip() for x in response])
            response = response.replace('&deg;', u'\u00B0')
            if 'boston' in dict(opts):
              response = response.replace('FUCKING','WICKED')
            irc.reply(response.encode('utf-8'), prefixNick=True)
        except:
            irc.reply("Man, I have no idea; things blew up real good.", prefixNick=True)

    forecast = wrap(forecast, [getopts({'boston':''}),'text'])

    def warnings(self, irc, msg, args, location):
      no_re = re.compile('^There are no')
      try:
          soup = self._fetch('http://forecast.weather.gov/zipcity.php?inputstring=%s' % location)
          href = soup.body('a',href=re.compile('=([A-Z]{3}[0-9]{3})'))[0]['href']
          zone_id = urlparse.parse_qs(urlparse.urlparse(href).query)['warnzone'][0]
          soup = self._fetch('http://alerts.weather.gov/cap/wwaatmget.php?x=%s' % zone_id)
          responses = [x.text.strip() for x in soup.findAll('title')]
          if no_re.match(responses[1]):
            response = responses[1] + responses[0][40:]
          else:
            response = '%s: %s' % (responses[0], ' ; '.join(responses[1:]))
          irc.reply(response, prefixNick=False)
      except Exception as error:
          irc.reply(detail)
          irc.reply("Man, I have no idea; things blew up real good.", prefixNick=True)

    warnings = wrap(warnings, ['text'])
      
Class = Forecast
