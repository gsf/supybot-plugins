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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os
import pygeoip
import socket

class IPLookupError(Exception):
    pass
    
class GeoIP(callbacks.Plugin):
    """Add the help for "@plugin help GeoIP" here
    This should describe *how* to use this plugin."""
    
    def _geoip(self, ip, msg=None):
        if ip == None:
            try:
                ip = socket.gethostbyname(msg.host)
            except:
                return { 'error' : 'IP address lookup failed' }
                
        g = pygeoip.GeoIP(os.path.dirname(__file__) + '/GeoLiteCity.dat')
        try:
            record = g.record_by_name(ip)
        except:
            record = None
        return record

    def _format_for_display(self, ip, template, msg=None):
        record = self._geoip(ip, msg)
        if record == None:
            return "No GeoIP information found for %s" % (ip)
        else:
            if 'error' in record:
                return record['error'].encode('utf8')
            else:
                if template == None:
                    return record.__str__()
                else:
                    return (template % record).encode('utf8')
        
    def ip_display(self, irc, msg, args):
        """[<ipaddress>|<hostname>] [<format_string>]
        Look up the GeoIP info for a given IP address and display it according to the given format string"""
        if len(args) == 2:
            ip = args[0]
            template = args[1]
        elif len(args) == 1:
            if args[0].find('%') >= 0:
                template = args[0]
                ip = None
            else:
                ip = args[0]
                template = None
        else:
            ip = None
            template = None
        irc.reply(self._format_for_display(ip, template, msg))
    display = ip_display
    
    def ip_latlong(self, irc, msg, args, ip):
        """[<ipaddress>|<hostname>]
        Look up the GeoIP latitude and longitude for a given IP address"""
        irc.reply(self._format_for_display(ip, '%(latitude)3.3f, %(longitude)3.3f', msg))
    latlong = ip_latlong = wrap(ip_latlong, [optional('text')])
        
    def ip_city(self, irc, msg, args, ip):
        """[<ipaddress>|<hostname>]
        Look up the GeoIP city/state/country for a given IP address"""
        record = self._geoip(ip, msg)
        if record == None:
            irc.reply("No GeoIP information found for %s" % (ip))
        else:
            if record['country_code3'] == 'USA' or record['country_code3'] == 'CAN':
                response = '%(city)s, %(region_name)s' % record
            else:
                response = '%(city)s, %(country_name)s' % record
            irc.reply(response.encode('utf8'))
    city = ip_city = wrap(ip_city, [optional('text')])
    
    def ip_zipcode(self, irc, msg, args, ip):
        """[<ipaddress>|<hostname>]
        Look up the GeoIP zip/postal code for a given IP address"""
        irc.reply(self._format_for_display(ip, '%(postal_code)s', msg))
    zipcode = ip_zipcode = postcode = ip_postcode = wrap(ip_zipcode, [optional('text')])
        
Class = GeoIP


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
