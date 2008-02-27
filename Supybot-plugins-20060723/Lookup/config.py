###
# Copyright (c) 2002-2005, Jeremiah Fincher
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

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import output, expect, anything, something, yn
    Lookup = conf.registerPlugin('Lookup', True)
    lookups = Lookup.lookups
    output("""This module allows you to define commands that do a simple key
              lookup and return some simple value.  It has a command "add"
              that takes a command name and a file from the data dir and adds a
              command with that name that responds with the mapping from that
              file. The file itself should be composed of lines
              of the form key:value.""")
    while yn('Would you like to add a file?'):
        filename = something('What\'s the filename?')
        try:
            fd = file(filename)
        except EnvironmentError, e:
            output('I couldn\'t open that file: %s' % e)
            continue
        counter = 1
        try:
            try:
                for line in fd:
                    line = line.rstrip('\r\n')
                    if not line or line.startswith('#'):
                        continue
                    (key, value) = line.split(':', 1)
                    counter += 1
            except ValueError:
                output('That\'s not a valid file; '
                       'line #%s is malformed.' % counter)
                continue
        finally:
            fd.close()
        command = something('What would you like the command to be?')
        conf.registerGlobalValue(lookups,command, registry.String(filename,''))
        nokeyVal = yn('Would you like the key to be shown for random '
                      'responses?')
        conf.registerGlobalValue(lookups.get(command), 'nokey',
                                    registry.Boolean(nokeyVal, ''))


Lookup = conf.registerPlugin('Lookup')
conf.registerGroup(Lookup, 'lookups')

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
