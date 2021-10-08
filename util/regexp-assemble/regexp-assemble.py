#! /usr/bin/env python

import sys;
import os;
import fileinput;
import re;
from subprocess import Popen, PIPE, TimeoutExpired

class Preprocessor(object):
	def __init__(self, script_path, args):
		self.callout = [script_path] + args

	def run(self, iterator):
		return self._preprocess(iterator, self._filter)

	def _preprocess(self, iterator, filter):
		proc = Popen(self.callout, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		for line in filter([line for line in iterator]):
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
	def _filter(self, lines):
		return lines

class LinePreprocessor(Preprocessor):
	def _filter(self, lines):
		return lines[0]

class BlockPreprocessor(Preprocessor):
	block_preprocessor_end_regex = re.compile(r'^##!<.*')

	def _filter(self, lines): 
		filtered = []
		for line in lines:
			if self.block_preprocessor_end_regex.match(line):
				break
			filtered.append(line)
		return filtered


script_directory = os.path.dirname(__file__)
preprocessor_map = {
	'cmdline': (FilePreprocessor, os.path.join(script_directory, 'regexp-cmdline.py')),
	'neglook': (BlockPreprocessor, os.path.join(script_directory, 'negativelookbehind.py'))
}
preprocessor_regex = re.compile(r'^##!>\s*(.*)')
# prefix, suffix, flags, block start block end
special_comment_markers = '^$+><'
simple_comment_regex = re.compile(r'^##![^' + special_comment_markers + r'].*')

def detect_preprocessor(line):
	match = preprocessor_regex.match(line)
	if match is None:
		return
		
	definition = match.group(1).split()
	try:
		processor_type, script_path = preprocessor_map[definition[0]]
		return processor_type(script_path, definition[1:])
	except KeyError:
		print(f'No processor found for {definition}')
		sys.exit(1)

def _is_simple_comment(line):
	return simple_comment_regex.match(line) is not None

def preprocess(lines):
	iterator = lines.__iter__()
	final_lines = []
	for processor_type in (LinePreprocessor, BlockPreprocessor, FilePreprocessor):
		transformed_lines = []
		line = next(iterator, None)
		while line is not None:
			if (_is_simple_comment(line)):
				line = next(iterator, None)
				continue
			processor = detect_preprocessor(line)
			if processor is None or not isinstance(processor, processor_type):
				transformed_lines.append(line)
				line = next(iterator, None)
				continue
			# skip the comment line
			next(iterator, None)
			transformed_lines += processor.run(iterator)
			line = next(iterator, None)

		final_lines = transformed_lines
		iterator = final_lines.__iter__()
	return final_lines


def assemble(lines):
	args = [os.path.join(script_directory, 'regexp-assemble.pl')]
	outs = None
	errs = None
	proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	for line in lines:
		proc.stdin.write(line.encode('utf-8'))
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
	
	sys.stdout.write(outs.decode('utf-8'))

def run():
	if len(sys.argv) < 2:
		print('no arguments provided. either pipe lines to this script or a list for file names')
		sys.exit(1)
	
	lines = preprocess(fileinput.input())
	assemble(lines)

if __name__ == '__main__':
	run()
