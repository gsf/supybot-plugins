** Supybot Dcc Plugin **

Requirements
--
In addition to Supybot, the Dcc plugin requires the Twisted core.

Usage
--
Load the plugin as normal, then initiate a DCC chat request with Supybot.
Authorized users will be given a persistent chat session over which commands
may be issued.

Capability
--
Use the "Dcc" capability to control who can use Dcc, for example:
"defaultcapability remove Dcc" to remove the capability by default.
 
