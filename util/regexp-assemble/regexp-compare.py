#!/usr/bin/env python

import os
import sys
import re
from math import ceil
from subprocess import PIPE, Popen, TimeoutExpired

script_directory_path = os.path.dirname(__file__)
rules_directory_path = os.path.join(os.path.dirname(os.path.dirname(script_directory_path)), 'rules')
script_path = os.path.join(script_directory_path, 'regexp-assemble.pl')

def check_file(file_name):
	if file_name.endswith('.data'):
		file_path = os.path.join(script_directory_path, file_name)
		proc = Popen([script_path, file_path], stdout=PIPE, stderr=PIPE)
		try:
			computed_regex, errs = proc.communicate(timeout=2)
			computed_regex = computed_regex.decode('utf-8').strip('\n').strip()
		except TimeoutExpired:
			proc.kill()
			print(f'Failed to run regexp-assemble.pl against {file_name}')
			sys.exit()
		
		rule_id = file_name.split('-')[1].split('.')[0]
		id_regex = re.compile(r'\s*[\'"]id:\s*' + rule_id + r'\s*,')
		rule_file_prefix = rule_id[:3]
		for rule_file_name in os.listdir(rules_directory_path):
			prefix = rule_file_name.split('-')[1]
			if prefix == rule_file_prefix:
				rule_file_path = os.path.join(rules_directory_path, rule_file_name)
				with open(rule_file_path, 'r') as handle:
					previous_line = None
					for line in handle:
						if id_regex.search(line) is not None:
							rx_line = previous_line
							if '@rx' not in rx_line:
								rx_line = line
								if '@rx' not in rx_line:
									print(f'Unable to find regex for rule {rule_id}')
									sys.exit()
							other, current_regex = rx_line.split('@rx')
							delimiter = other.strip()[-1]
							current_regex = current_regex.strip()
							last = None
							for index, character in enumerate(current_regex):
								if character == delimiter and last != '\\':
									current_regex = current_regex[:index]
									break
								last = character
							
							if current_regex == computed_regex:
								print(f'Regex of {rule_id} has not changed')
							else:
								print(f'Regex of {rule_id} has changed!')
								max_chunks = ceil(max(len(current_regex), len(computed_regex)) / 50)
								for index in range(0, max_chunks * 50, 50):
									end_index = min(len(current_regex), index + 50)
									if end_index > index:
										sys.stdout.write('\ncurrent:  ')
										chunk = current_regex[index:end_index]
										sys.stdout.write(chunk)
										sys.stdout.write(f'({int(index / 50) + 1} / {ceil(len(current_regex) / 50)})'.rjust(60 - len(chunk)))
									end_index = min(len(computed_regex), index + 50)
									if end_index > index:
										sys.stdout.write('\ncomputed: ')
										chunk = computed_regex[index:end_index]
										sys.stdout.write(chunk)
										sys.stdout.write(f'({int(index / 50) + 1} / {ceil(len(current_regex) / 50)})'.rjust(60 - len(chunk)))
									sys.stdout.write('\n')
								sys.stdout.write('\n')
							break
						previous_line = line

def run():
	for file_name in os.listdir(script_directory_path):
		check_file(file_name)

if __name__ == '__main__':
	if len(sys.argv) > 1:
		for file_name in sys.argv[1:]:
			check_file(file_name)
	else:
		run()