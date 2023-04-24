#!/bin/bash
#
# OWASP ModSecurity Core Rule Set helper script
#
# This script creates the data file user-agents-automated-agents.data
#

cat user-agents-automated-agents.src user-agents-automated-agents-crs.src | \
	sort > user-agents-automated-agents.data

