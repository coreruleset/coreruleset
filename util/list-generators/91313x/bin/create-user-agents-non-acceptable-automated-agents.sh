#!/bin/bash
#
# OWASP ModSecurity Core Rule Set helper script
#
# This script creates the data file user-agents-non-acceptable-automated-agents.data
#

cat user-agents-automated-agents.src | \
	grep -F -v -f acceptable-bots-cloudflare.src | \
	grep -F -v -f acceptable-bots-mitchellkrogza.src | \
	grep -E -v -f acceptable-bots-crs.src |
	sed -e "/^#/d" \
	    -e "/^$/d" \
	>  user-agents-non-acceptable-automated-agents.data
