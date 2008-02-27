I discovered that Freenode has an interesting feature that allows a
client to know whether a person is identified by prefixing a '+' to
the beginning of all messages sent by identified clients.  I thought
this might be an interesting feature to exploit, for instance, by
making the bot always ignore all messages (even in public channels)
from un-identified people.  This plugin is proof of that concept.

Another possibility, as yet unimplemented, is the possibility of
automatically registering users whose names match the nick of all
identified messages, and automatically recognizing messages from that
nick (when it is identified, of course) as being from that user.
Some other intrepid soul will have to try that out, though.
