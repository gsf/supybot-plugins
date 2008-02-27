###
# Copyright (c) 2005, Ali Afshar
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
import supybot.registry as registry

import gwplugins

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Gateway', True)


Gateway = conf.registerPlugin('Gateway')

conf.registerGlobalValue(Gateway, 'capability',
	registry.String('owner', """The default capability to connect to the gateway and use it."""))
conf.registerGlobalValue(Gateway, 'motd',
    registry.String('Welcome to the Supybot Gateway', """This is the
    message returned to clients on successful authorization."""))

conf.registerGroup(Gateway, 'keys')

conf.registerGlobalValue(Gateway.keys, 'rsaKeyFile',
	registry.String('id-rsa',
	"""Filename of RSA key file for use for SSH."""))

conf.registerGlobalValue(Gateway.keys, 'sslCertificateFile',
	registry.String('server.pem',
	"""Filename of SSL certifcate file."""))

conf.registerGlobalValue(Gateway.keys, 'sslKeyFile',
	registry.String('privkey.pem',
	"""Filename of SSL private key file."""))

#conf.registerGroup(Gateway, 'protocols')

for p in gwplugins.plugins:
	protocolGroup = conf.registerGroup(Gateway, p.PROTOCOL)
	conf.registerGlobalValue(protocolGroup, 'defaultPort',
		registry.Integer(p.DEFAULT_PORT,
		"""The port that this daemon will start on if started without argument."""))
	conf.registerGlobalValue(protocolGroup, 'autoStart',
		registry.Boolean(False,
		"""Determines whether the interface will start automatically."""))
	conf.registerGlobalValue(protocolGroup, 'capability',
		registry.String(p.CAPABILITY,
		"""Determines what capability users will require to connect to the protocol.
			If this value is an empty string, no capability will be checked."""))
	conf.registerGlobalValue(protocolGroup, 'useSSL',
		registry.Boolean(True,
		"""Determines whther the interface will attempt to use SSL."""))
	extraGroups = {}
	for i in p.CONFIG_EXTRA:
		n, t, v, h = i
		if n.startswith('@'):
                    n = n[1:]
                    extraGroups[n] = conf.registerGroup(protocolGroup, n)
                else:
                    g = protocolGroup
                    if n.count('.') > 0:
                        gn, n = n.split('.')
			g = extraGroups[gn]
                    conf.registerGlobalValue(g, n,
			getattr(registry, t)(v, h))

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
