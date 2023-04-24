#!/bin/bash
#
# OWASP ModSecurity Core Rule Set helper script
#
# This script is used to retrieve a list of user agents of good bots.
# The script also transforms the strings it receives and prints them via STDOUT.
#

CURL_OPTIONS="--silent"

curl $CURL_OPTIONS https://raw.githubusercontent.com/mitchellkrogza/apache-ultimate-bad-bot-blocker/master/Apache_2.4/custom.d/globalblacklist.conf -s | \
	grep BrowserMatchNoCase | \
	grep good_bot | \
	cut -d\" -f2 | \
	cut -b7- | \
	tr "[A-Z]" "[a-z]" | \
	sed \
        	-e "s/wget\/[0-9.]*/wget/" \
        	-e "s/uptimerobot\/[0-9.]*/uptimerobot/" \
       		-e "s/kraken\/[0-9.]*/kraken/" \
        	-e "s/sffeedreader\/[0-9.]*/sffeedreader/" | \
	sed -e "s/(?:.*//" -e "s/\\\ / /g" | \
	sort > acceptable-bots-mitchellkrogza.src


