#! /usr/bin/env python

# This script is a simple wrapper around regexp-assemble.pl, regexp-cmdline.py, and
# regexp-negativelookbehind.py. It takes a rule id, data file name or data file path
# as input and runs it through the scripts, depending on the marker flags present in
# the data file. The last step is to always run the output through regexp-assemble.pl.
#
# Preprocessors are defined in this file. To add a new preprocessor, add an entry to
# the preprocessor_map. The key of the entry is the keyword used in the data file
# and the value is the script you want to execute (expected to be in the lib directory).

from distutils.command.build import build
from distutils.log import error
from logging import root
import sys;
import os;
import fileinput;
import re;
from subprocess import Popen, PIPE, TimeoutExpired
import argparse
from typing import TextIO, Mapping
import msc_pyparser
from math import ceil

class Assembler(object):	
	script_directory = os.path.dirname(__file__)
	lib_directory = os.path.join(script_directory, 'lib')
	special_comment_markers = '^$+><'
	simple_comment_regex = re.compile(r'^##![^' + special_comment_markers + r'].*')
	# prefix, suffix, flags, block start block end
	preprocessor_regex = re.compile(r'^##!>\s*(.*)')

	def __init__(self):
		self.preprocessor_map = {
			'cmdline': (FilePreprocessor, os.path.join(self.lib_directory, 'regexp-cmdline.py')),
		}

	def run(self, file: str) -> bytes:
		with open(file, 'r') as handle:
			iterator = handle.readlines().__iter__()
			lines = self.preprocess(iterator)
		if len(lines) == 0:
			print('No input. Either pass a filename, a rule id or pipe data to the script')
			sys.exit(1)
		return self.assemble(lines)

	def detect_preprocessor(self, line):
		match = self.preprocessor_regex.match(line)
		if match is None:
			return
			
		definition = match.group(1).split()
		try:
			processor_type, script_path = self.preprocessor_map[definition[0]]
			return processor_type(script_path, definition[1:])
		except KeyError:
			print(f'No processor found for {definition}')
			sys.exit(1)

	def _is_simple_comment(self, line):
		return self.simple_comment_regex.match(line) is not None

	def preprocess(self, lines):
		iterator = lines.__iter__()
		final_lines = []
		for processor_type in (LinePreprocessor, BlockPreprocessor, FilePreprocessor):
			transformed_lines = []
			line = next(iterator, None)
			while line is not None:
				if (self._is_simple_comment(line)):
					line = next(iterator, None)
					continue
				processor = self.detect_preprocessor(line)
				if processor is None or not isinstance(processor, processor_type):
					transformed_lines.append(line)
					line = next(iterator, None)
					continue
				transformed_lines += processor.run(iterator)
				line = next(iterator, None)

			final_lines = transformed_lines
			iterator = final_lines.__iter__()
		return final_lines


	def assemble(self, lines) -> bytes:
		args = [os.path.join(self.lib_directory, 'regexp-assemble.pl')]
		outs = None
		errs = None
		proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		for line in lines:
			proc.stdin.write(line.encode('utf-8'))
			proc.stdin.write(b'\n')
		try:
			outs, errs = proc.communicate(timeout=30)
		except TimeoutExpired:
			proc.kill()
			print(f'Assembling regex timed out')
			print('Stderr: ' + errs.decode('utf-8'))
			sys.exit(1)

		if errs:
			print('Failed to assemble regex')
			print('Stderr: ' + errs.decode('utf-8'))
			sys.exit(1)
		
		return outs

class Parser(object):
	rule_id_regex = re.compile(r'^(\d{6})')
	script_directory = os.path.dirname(__file__)
	data_directory = os.path.join(script_directory, 'data')
	root_directory = os.path.dirname(os.path.dirname(script_directory))
	rules_directory = os.path.join(root_directory, 'rules')
	parsers: Mapping[str, msc_pyparser.MSCParser] = {}
	prefix_to_file_map: Mapping[str, str] = {}

	def perform_compare_or_update(self, rule_id: str=None, func=None):
		files = os.listdir(self.data_directory)
		files.sort()
		assembler = Assembler()
		if rule_id:
			for file in files:
				if rule_id in file:
					self.process_regex(os.path.join(self.data_directory, file), assembler, func)
					break
		else:
			for file in files:
				self.process_regex(os.path.join(self.data_directory, file), assembler, func)
		

	def process_regex(self, file, assembler, func):
		regex = assembler.run(file).decode('utf-8').split('\n')[0]
		rule_id = self.rule_id_regex.match(os.path.basename(file)).group(1)
		print(f'Processing {rule_id}')
		rule_prefix = rule_id[:3]
		if rule_prefix in self.parsers:
			parser = self.parsers[rule_prefix]
		else:
			for rule_file in os.listdir(self.rules_directory):
				if rule_prefix in rule_file:
					self.prefix_to_file_map[rule_prefix] = rule_file
					with open(os.path.join(self.rules_directory, rule_file), 'r') as handle:
						parser = msc_pyparser.MSCParser()
						self.parsers[rule_prefix] = parser
						parser.parser.parse(handle.read())
						break
			if not parser:
				raise Warning(f'No rule file found for data file {file}')
		
		for config in parser.configlines:
			if config['type'] == 'SecRule':
				for action in config['actions']:
					if action['act_name'] == 'id' and action['act_arg'] == rule_id:
						func(rule_id, regex, config['operator_argument'], config, 'operator_argument')
						break


class Comparer(Parser):
	def run(self, rule_id: str):
		self.perform_compare_or_update(rule_id, self.compare_regex)

	def run_all(self):
		self.perform_compare_or_update(None, self.compare_regex)

	def compare_regex(self, rule_id: str, generated_regex: str, current_regex: str, config: dict, config_key: str):
		if current_regex == generated_regex:
			print(f'Regex of {rule_id} has not changed')
		else:
			print(f'Regex of {rule_id} has changed!')
			diff_found = False
			max_chunks = ceil(max(len(current_regex), len(generated_regex)) / 50)
			for index in range(0, max_chunks * 50, 50):
				end_index = min(len(current_regex), index + 50)
				if end_index > index:
					current_chunk = current_regex[index:end_index]
				end_index = min(len(generated_regex), index + 50)
				if end_index > index:
					generated_chunk = generated_regex[index:end_index]
				
				print_first_diff = not diff_found and current_chunk and generated_chunk and current_chunk != generated_chunk
				if print_first_diff:
					diff_found = True
					sys.stdout.write('\n===========\nfirst difference\n-----------')
				if current_chunk:
					sys.stdout.write('\ncurrent:  ')
					sys.stdout.write(current_chunk.rjust(len(current_chunk) + 5))
					sys.stdout.write(f'({int(index / 50) + 1} / {ceil(len(current_regex) / 50)})'.rjust(65 - len(current_chunk)))
				if generated_chunk:
					sys.stdout.write('\ngenerated: ')
					sys.stdout.write(generated_chunk.rjust(len(generated_chunk) + 4))
					sys.stdout.write(f'({int(index / 50) + 1} / {ceil(len(current_regex) / 50)})'.rjust(65 - len(generated_chunk)))
					sys.stdout.write('\n')
				if print_first_diff:
					sys.stdout.write('===========\n')

			sys.stdout.write('\n')

class Updater(Parser):
	def run(self, rule_id: str):
		self.perform_compare_or_update(rule_id, self.update_regex)
		self.write_updates()

	def run_all(self):
		self.perform_compare_or_update(None, self.update_regex)

	def update_regex(self, rule_id: str, generated_regex: str, current_regex: str, config: dict, config_key: str):
		config[config_key] = generated_regex

	def write_updates(self):
		for rule_prefix, parser in self.parsers.items():
			writer = msc_pyparser.MSCWriter(parser.configlines)
			file_path = os.path.join(self.rules_directory, self.prefix_to_file_map[rule_prefix])
			with open(file_path, "w") as handle:
				writer.generate()
				# add extra new line at the end of file
				writer.output.append("")
				handle.write("\n".join(writer.output))
class Preprocessor(object):
	def __init__(self, script_path, args):
		self.callout = [script_path] + args

	def run(self, iterator):
		return self._preprocess(iterator, self._filter)

	def _preprocess(self, iterator, filter):
		proc = Popen(self.callout, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		for line in filter(iterator):
			proc.stdin.write(line.encode('utf-8'))
		
		errs = None
		try:
			outs, errs = proc.communicate(timeout=30)
		except TimeoutExpired:
			proc.kill()
			print(f'Callout timed out: {self.callout}')
			print('Stderr: ' + errs.decode('utf-8'))
			sys.exit(1)
		return outs.decode('utf-8').splitlines()
	


class FilePreprocessor(Preprocessor):
	def _filter(self, iterator):
		for line in iterator:
			yield line

class LinePreprocessor(Preprocessor):
	def _filter(self, iterator):
		yield next(iterator)

class BlockPreprocessor(Preprocessor):
	block_preprocessor_end_regex = re.compile(r'^##!<.*')

	def _filter(self, iterator): 
		line = next(iterator, None)
		while line is not None and not self.block_preprocessor_end_regex.match(line):
			yield line
			line = next(iterator, None)



def build_args_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description='Utilities for generating and managing regular expressions in CRS rule files')
	subparsers = parser.add_subparsers()
	build_generate_args_parser(subparsers)
	build_update_args_parser(subparsers)
	build_compare_args_parser(subparsers)

	return parser

def build_generate_args_parser(subparsers):
	parser = subparsers.add_parser('generate')
	parser.add_argument('rule_id', action=RuleNameParser)
	parser.set_defaults(func=handle_generate)

def build_update_args_parser(subparsers):
	parser = subparsers.add_parser('update')
	parser.add_argument('rule_id', nargs='?', action=RuleNameParser, default=None)
	parser.add_argument('--all', action='store_true')
	parser.set_defaults(func=handle_update)

def build_compare_args_parser(subparsers):
	parser = subparsers.add_parser('compare')
	parser.add_argument('rule_id', nargs='?', action=RuleNameParser, default=None)
	parser.add_argument('--all', action='store_true')
	parser.set_defaults(func=handle_compare)

def handle_generate(namespace: argparse.Namespace):
	script_directory = os.path.dirname(__file__)
	if namespace.rule_id:
		with open(os.path.join(script_directory, 'data', f'{namespace.rule_id}.data')) as handle:
			file = handle
	elif 'stdin' in namespace:
		file = namespace.stdin
	else:
		raise argparse.ArgumentError('Unhandled combination of arguments')
	Assembler().run(file)

def handle_update(namespace: argparse.Namespace):
	if namespace.rule_id:
		Updater().run(namespace.rule_id)
	elif namespace.all:
		Updater().run_all()




def handle_compare(namespace: argparse.Namespace):
	if namespace.rule_id:
		Comparer().run(namespace.rule_id)
	elif namespace.all:
		Comparer().run_all()

class RuleNameParser(argparse.Action):
	def __init__(self,
			option_strings,
			dest,
			nargs=None,
			default=None,
			required=False):
		super().__init__(
			option_strings,
			dest,
			nargs=nargs,
			default=default,
			required=required)
	
	def __call__(self,
			parser: argparse.ArgumentParser,
			namespace: argparse.Namespace,
			values: list,
			option_string: str):
		if values == '-':
			setattr(namespace, 'stdin', sys.stdin)
			return
		elif not values:
			if self.nargs == '?' and not namespace.all:
				raise ValueError('Invalid arguments')
			return
		
		match = re.fullmatch(r'(\d{6})(?:\.data)?', values)
		if not match:
			raise ValueError(f'Failed to identify rule from argument {values}')
		setattr(namespace, self.dest, match.group(1))

if __name__ == '__main__':
	namespace = build_args_parser().parse_args()
	namespace.func(namespace)
