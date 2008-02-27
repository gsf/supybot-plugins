ExternalNotice Plugin README
--

Requirements
--
1. Twisted (core only required)

Installation
--
Place plugin directory in a configured plugin directory (as usual).

Usage
--
Once installed, load the plugin as usual. Now, the supybot user can issue
notices for supybot to emit on a channel and network it is on, by using the
provided supybot-external-notice.py script.

The script has the following usage parameters:

usage: supybot-external-notice.py [options] <network> <channel>

options:
  -h, --help            show this help message and exit
  -s, --stdin           Read notice data from stdin.
  -f FORMATTER, --formatter=FORMATTER
                        formatter to apply to notice body

The plugin has no commands, and no configuration variables.

Under the hood
--
ExternalNotice uses the UDP protocol over a Unix Domain Socket which is
started in ~/.supybot-external-notice for the supybot user.

Security
--
The socket is set to be user-only writeable, and unreadable. This is to ensure
that only the supybot user can connect to the plugin and issue commands. This
behaviour can be changes by modifying the permissions set on the socket.

As always
--
Bugs, suggestions, criticism, advice, improvements and frankenstein-ideas to
aafshar@gmail.com, or #supybot on freenode.

All the best,

Ali
