I wrote this plugin because I wanted a bot I run (but don't normally
interact with) to send me periodic emails with its status.  Combined
with the Scheduler and Status plugins, this did the trick.  I did
something like this::

  @scheduler repeat email-status [seconds 1h] "utilities ignore [postman send jemfinch@supybot.com [format join \"\n\n\"[uptime] [cpu] [cmd] [threads] [net]]]"

Works like a charm -- every hour I get an update email.  If I don't
get any for a significant amount of time, I can go check on the bot.
