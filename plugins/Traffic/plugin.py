import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
import urllib
import time
from urllib2 import build_opener, HTTPError
from string import capitalize

class Traffic(callbacks.Privmsg):
    def traffic(self, irc, msg, args):
        """[--map] <location>

        Returns the traffic conditions for a given location.
        """
        show_maps = False
        if len(args) == 0:
            irc.reply('usage: traffic [--map] <location>')
            return 
        if args[0] == '--map':
            show_maps = True
            args.pop(0)
            # this is homely
            if len(args) == 0:
                irc.reply('usage: traffic [--map] <location>')
        location = ' '.join(args)
        url = 'http://local.yahooapis.com/MapsService/V1/trafficData?appid=YahooDemo&location=%s&include_map=1' % (urllib.quote(location))
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        # yes, this is poor design
        xml = None
        try:
            xml = opener.open(url)
        except HTTPError, error:
            # yes, this duplication is ugly
            response = 'http error %s for %s' % (error.code, location)
            xml_str = xml.read()
            soup = BeautifulSoup(xml_str)
            error_message = soup.find('message')
            if error_message:
                irc.reply('%s: %s' % (response, error_message.string), prefixNick=True)
            return
        xml_str = xml.read()
        soup = BeautifulSoup(xml_str)
        results = soup.findAll('result')
        if len(results) == 0:
            irc.reply('no results!', prefixNick=True)
            return
        else:
            responses = []
            for result in results:
                type = result['type']
                title = result.title.string
                description = result.description.string
                last_updated = time.ctime(float(result.updatedate.string))
                image_url = result.imageurl.string
                if show_maps:
                    responses.append('%s: %s (%s) [%s] <%s>' % (capitalize(type), title, description, 
                                                                last_updated, image_url))
                else:
                    responses.append('%s: %s (%s) [%s]' % (capitalize(type), title, description, 
                                                                last_updated))
            irc.reply(" | ".join(responses), prefixNick=True)

Class = Traffic

"""
example url: http://local.yahooapis.com/MapsService/V1/trafficData?appid=YahooDemo&location=08901&include_map=1

error looks like this:

<Error>
  The following errors were detected:
  <Message>location is out of range</Message>
</Error>

result from yahoo should look like this:
 
<ResultSet xsi:schemaLocation="urn:yahoo:maps http://api.local.yahoo.com/MapsService/V1/TrafficDataResponse.xsd">
  <LastUpdateDate>1204744572</LastUpdateDate>
  <Result type="incident">
    <Title>Lane closed, on US-1 NB at PIERSON AVE</Title>
    <Description>
        SCHEDULED WORK CREW; RIGHT LANE CLOSED; TWO LANES MAINTAINED AND AGAIN FROM GRANDVIEW AVE  EDISON  TO FORD AVE  WOODBRIDGE  UNTIL 2009  MIDDLESEX COUNTY ; STAY LEFT.
    </Description>
    <Latitude>40.532060</Latitude>
    <Longitude>-74.349090</Longitude>
    <Direction>NB</Direction>
    <Severity>2</Severity>
    <ReportDate>1168286345</ReportDate>
    <UpdateDate>1199243627</UpdateDate>
    <EndDate>1262290919</EndDate>
    <ImageUrl>
        http://gws.maps.yahoo.com/mapimage?MAPDATA=tCe4wOd6wXVmWv2oMMBZg2mqo7Wi2BQmoTBCW9RkhYnJppn4exsPvzQO2Be5zMCVDF685wsArOlTSePkiUUGaAsJ1hcsi0wSdmZhV7T.nO.Gz18P40C9fUOAv3Loe9hK_s8P0VlcgbYkDM79BUJvPSPVZTcHQtDiQJFB2flC85apqSTs.q4ASxbbOvv_weC8Dw--&mvt=m?cltype=onnetwork&.intl=us
    </ImageUrl>
  </Result>
</ResultSet>
"""
