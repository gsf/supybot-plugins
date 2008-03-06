import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from BeautifulSoup import BeautifulSoup
import urllib
import time
from urllib2 import build_opener
from string import upper


class Traffic(callbacks.Privmsg):
    def traffic(self, irc, msg, args):
        """[[street,] city, state,] zip

        Returns the traffic conditions for a given location.
        """
        # example url: http://local.yahooapis.com/MapsService/V1/trafficData?appid=YahooDemo&location=08901&include_map=1
        if len(args) == 0:
            irc.reply('usage: traffic <location>')
            return
        location = ' '.join(args)
        url = 'http://local.yahooapis.com/MapsService/V1/trafficData?appid=YahooDemo&location=%s&include_map=1' % (urllib.quote(location))
        ua = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20071204 Ubuntu/7.10 (gutsy) Firefox/2.0.0.11'
        opener = build_opener()
        opener.addheaders = [('User-Agent', ua)]
        xml = opener.open(url)
        xml_str = xml.read()
        soup = BeautifulSoup(xml_str)
        results = soup.findAll('result')
        if len(results) == 0:
            irc.reply('no results', prefixNick=True)
        else:
            responses = []
            for result in results:
                type = result['type']
                title = result.title.string
                description = result.description.string
                last_updated = time.ctime(float(result.updatedate.string))
                image_url = result.imageurl.string
                responses.append('%s: %s (%s) [%s] <%s>' % (upper(type), title, description, 
                    last_updated, image_url))
            irc.reply(" | ".join(responses), prefixNick=True)

Class = Traffic

"""
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
