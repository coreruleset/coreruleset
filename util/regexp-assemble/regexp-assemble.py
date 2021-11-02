#! /usr/bin/env python

# This script is a simple wrapper around regexp-assemble.pl, regexp-cmdline.py, and
# regexp-negativelookbehind.py. It takes a rule id, data file name or data file path
# as input and runs it through the scripts, depending on the marker flags present in
# the data file. The last step is to always run the output through regexp-assemble.pl.
#
# Preprocessors are defined in this file. To add a new preprocessor, add an entry to
# the preprocessor_map. The key of the entry is the keyword used in the data file
# and the value is the script you want to execute (expected to be in the lib directory).

import sys;
import os;
import fileinput
import re;
from subprocess import Popen, PIPE, TimeoutExpired

class Preprocessor(object):
	def __init__(self, script_path, allowed_keywords, args):
		for arg in args:
			if arg not in allowed_keywords:
				print(f'Keywoard "{arg}" not allowed in this context')
				sys.exit(1)
		effective_args = [arg for arg in args if allowed_keywords[arg]]
		self.callout = [script_path] + effective_args
		self._args = args
		self._allowed_keywords = allowed_keywords

	def run(self, iterator):
		preprocessed = self._preprocess(iterator, self._filter)
		return self._postprocess(preprocessed)

	def _preprocess(self, iterator, filter):
		proc = Popen(self.callout, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		for line in filter(iterator):
			proc.stdin.write(line.encode('utf-8'))
		
		errs = None
		try:
			outs, errs = proc.communicate(timeout=30)
			if len(errs) > 0:
				sys.stderr.write(f'Callout failed: {self.callout}')
				sys.stderr.writelines(errs.decode('utf-8'))
				sys.exit(1)
		except TimeoutExpired:
			proc.kill()
			print(f'Callout timed out: {self.callout}')
			print('Stderr: ' + errs.decode('utf-8'))
			sys.exit(1)
		return outs.decode('utf-8').splitlines()
	
	def _postprocess(self, output):
		return output
	


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

	def _postprocess(self, output):
		if 'prefix' in self._args:
			assert len(output) <= 1
			return ['##!^ ' + line for line in output]
		elif 'suffix' in self._args:
			assert len(output) <= 1
			return ['##!$ ' + line for line in output]
		else:
			return output



script_directory = os.path.dirname(__file__)
lib_directory = os.path.join(script_directory, 'lib')
preprocessor_map = {
	# directive name : (processor type, path to script, allowed keywords (True: pass to script))
	'cmdline': (BlockPreprocessor, os.path.join(lib_directory, 'regexp-cmdline.py'), {'windows': True, 'unix': True}),
	'assemble': (BlockPreprocessor, os.path.join(script_directory, 'regexp-assemble.py'), {'prefix': False, 'suffix': False})
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
		processor_type, script_path, allowed_keywords = preprocessor_map[definition[0]]
		return processor_type(script_path, allowed_keywords, definition[1:])
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
			if (len(line.strip()) == 0 or _is_simple_comment(line)):
				line = next(iterator, None)
				continue
			processor = detect_preprocessor(line)
			if processor is None or not isinstance(processor, processor_type):
				transformed_lines.append(line)
				line = next(iterator, None)
				continue
			transformed_lines += processor.run(iterator)
			line = next(iterator, None)

		final_lines = transformed_lines
		iterator = final_lines.__iter__()
	return final_lines


def assemble(lines):
	args = [os.path.join(lib_directory, 'regexp-assemble.pl')]
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
		sys.stderr.write('Failed to assemble regex\n')
		sys.stderr.write('Stderr: ' + errs.decode('utf-8') + '\n')
		sys.exit(1)

	sys.stdout.write(outs.decode('utf-8'))

def run():
	if len(sys.argv) > 1 and re.fullmatch(r'\d{6}(?:[^.]+)?', sys.argv[1]):
		with open(os.path.join(script_directory, 'data', sys.argv[1] + '.data')) as handle:
			iterator = handle.readlines().__iter__()
	else:
		iterator = fileinput.input()

	lines = preprocess(iterator)
	if len(lines) == 0:
		sys.stderr.write('No input. Either pass a filename, a rule id or pipe data to the script\n')
		sys.exit(1)
	assemble(lines)

if __name__ == '__main__':
	run()