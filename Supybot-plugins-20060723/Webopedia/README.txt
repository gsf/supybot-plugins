Webopedia Supybot Plugin

Written By:
Kevin Murphy, aka Skorobeus

Usage Instructions:

----
  webopedia <term>
----

Issuing the webopedia command with a term will fetch the definition for that 
term from Webopedia.com (if that term is defined there) and display it to the
user.

Issuing the webopedia command without a term will fetch the "Term of the Day"
and display it and its definition to the user.

----
  http://www.webopedia.com/TERM/R/RAID.html
----

The plugin will optionally snarf URLs to Webopedia definition pages, if 
plugins.webopedia.termSnarfer is True for a given channel.