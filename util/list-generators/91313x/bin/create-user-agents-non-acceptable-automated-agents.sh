#!/bin/bash
#
# OWASP ModSecurity Core Rule Set helper script
#
# This script prints the merged list of non-acceptable automated agents.
#

cat user-agents-automated-agents.src | \
	grep -F -v -f acceptable-bots-cloudflare.src | \
	grep -F -v -f acceptable-bots-mitchellkrogza.src | \
	grep -E -v -f acceptable-bots-crs.src |
	sed -e "/^#/d" \
	    -e "/^$/d"
