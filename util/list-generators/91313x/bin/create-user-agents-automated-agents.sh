#!/bin/bash
#
# OWASP ModSecurity Core Rule Set helper script
#
# This script prints the merged list automated agents.
#

cat user-agents-automated-agents.src user-agents-automated-agents-crs.src | \
	sort

