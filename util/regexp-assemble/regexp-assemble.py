#! /usr/bin/env python3

# This script is a simple wrapper around regexp-assemble.pl, regexp-cmdline.py, and
# regexp-negativelookbehind.py. It takes a rule id, data file name or data file path
# as input and runs it through the scripts, depending on the marker flags present in
# the data file. The last step is to always run the output through regexp-assemble.pl.
#
# Preprocessors are defined in this file. To add a new preprocessor, add an entry to
# the preprocessor_map. The key of the entry is the keyword used in the data file
# and the value is the script you want to execute (expected to be in the lib directory).

<<<<<<< HEAD
import sys;
import os;
import fileinput
import re;
from subprocess import Popen, PIPE, TimeoutExpired
||||||| 6692cb92
import sys;
import os;
import fileinput;
import re;
from subprocess import Popen, PIPE, TimeoutExpired
=======
import os, re, sys
import argparse
import logging
from typing import TypeVar
>>>>>>> unified-regex-utils

<<<<<<< HEAD
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
||||||| 6692cb92
class Preprocessor(object):
	def __init__(self, script_path, args):
		self.callout = [script_path] + args
=======
from lib.operators.assembler import Assembler
from lib.operators.comparer import Comparer
from lib.operators.updater import Updater
from lib.context import Context
>>>>>>> unified-regex-utils

<<<<<<< HEAD
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
	
||||||| 6692cb92
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
	
=======
S = TypeVar("S", bound="argparse._SubParserAction[argparse.ArgumentParser]")
>>>>>>> unified-regex-utils


def build_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Utilities for generating and managing regular expressions in CRS rule files"
    )
    levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=levels,
        help="Change the log level; default is INFO",
    )

    subparsers = parser.add_subparsers()
    build_generate_args_parser(subparsers)
    build_update_args_parser(subparsers)
    build_compare_args_parser(subparsers)

    return parser

	def _postprocess(self, output):
		if 'prefix' in self._args:
			assert len(output) <= 1
			return ['##!^ ' + line for line in output]
		elif 'suffix' in self._args:
			assert len(output) <= 1
			return ['##!$ ' + line for line in output]
		else:
			return output


<<<<<<< HEAD

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
||||||| 6692cb92

script_directory = os.path.dirname(__file__)
lib_directory = os.path.join(script_directory, 'lib')
preprocessor_map = {
	'cmdline': (FilePreprocessor, os.path.join(lib_directory, 'regexp-cmdline.py')),
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
			transformed_lines += processor.run(iterator)
			line = next(iterator, None)

		final_lines = transformed_lines
		iterator = final_lines.__iter__()
	return final_lines
=======
def build_generate_args_parser(subparsers: S):
    parser = subparsers.add_parser(
        "generate",
        help="Generate regular expression from a data file",
        description="""
    Generate regular expression from a data file.
    This command is mainly used for quick debugging.
    It prints the generated regular expression to stdout.""",
    )
    parser.add_argument(
        "rule_id",
        action=RuleNameParser,
        help="""
    The six digit ID of the rule, e.g. 932100.
    The special token `-` will cause the script to accept input
    from stdin.
    """,
    )
    parser.set_defaults(func=handle_generate)
>>>>>>> unified-regex-utils


def build_update_args_parser(subparsers: S):
    parser = subparsers.add_parser(
        "update",
        help="Update regular expressions in rule files",
        description="""
    Update regular expressions in rule files.
    This command will generate regulare expressions from the data
    files and update the associated rule.
    """,
    )
    parser.add_argument(
        "rule_id",
        nargs="?",
        action=RuleNameParser,
        default=None,
        help="The six digit ID of the rule, e.g. 932100",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="""
    Instead of supplying a rule_id, you can tell the script to
    update all rules from their data files
    """,
    )
    parser.set_defaults(func=handle_update)

<<<<<<< HEAD
	if errs:
		sys.stderr.write('Failed to assemble regex\n')
		sys.stderr.write('Stderr: ' + errs.decode('utf-8') + '\n')
		sys.exit(1)

	sys.stdout.write(outs.decode('utf-8'))
||||||| 6692cb92
	if errs:
		print('Failed to assemble regex')
		print('Stderr: ' + errs.decode('utf-8'))
		sys.exit(1)
	
	sys.stdout.write(outs.decode('utf-8'))
=======
>>>>>>> unified-regex-utils

def build_compare_args_parser(subparsers: S):
    parser = subparsers.add_parser(
        "compare",
        help="Compare generated regular expressions with the contents of associated rules",
        description="""
    Compare generated regular expressions with the contents of associated
    rules.
    This command is mainly used for debugging.
    It prints regular expressions in fixed sized chunks and detects the
    first change.
    You can use this command to quickly check whether any rules are out of
    sync with their data file.
    """,
    )
    parser.add_argument(
        "rule_id",
        nargs="?",
        action=RuleNameParser,
        default=None,
        help="The six digit ID of the rule, e.g. 932100",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="""
    Instead of supplying a rule_id, you can tell the script to
    compare all regular expressions
    """,
    )
    parser.set_defaults(func=handle_compare)

<<<<<<< HEAD
	lines = preprocess(iterator)
	if len(lines) == 0:
		sys.stderr.write('No input. Either pass a filename, a rule id or pipe data to the script\n')
		sys.exit(1)
	assemble(lines)
||||||| 6692cb92
	lines = preprocess(iterator)
	if len(lines) == 0:
		print('No input. Either pass a filename, a rule id or pipe data to the script')
		sys.exit(1)
	assemble(lines)
=======
>>>>>>> unified-regex-utils

<<<<<<< HEAD
if __name__ == '__main__':
	run()
||||||| 6692cb92
if __name__ == '__main__':
	run()
=======
def handle_generate(namespace: argparse.Namespace):
    context = create_context()
    assembler = Assembler(context)

    if namespace.rule_id:
        with open(
            os.path.join(context.data_files_directory, f"{namespace.rule_id}.data"),
            "rt",
        ) as handle:
            regex = assembler.run(handle)
    elif "stdin" in namespace:
        regex = assembler.run(namespace.stdin)
    else:
        raise argparse.ValueError("Unhandled combination of arguments")

    sys.stdout.write(regex)
    sys.stdout.write("\n")


def handle_update(namespace: argparse.Namespace):
    updater = Updater(create_context())
    if namespace.rule_id:
        updater.run(namespace.rule_id)
    elif namespace.all:
        updater.run_all()


def handle_compare(namespace: argparse.Namespace):
    comparer = Comparer(create_context())
    if namespace.rule_id:
        comparer.run(namespace.rule_id)
    elif namespace.all:
        comparer.run_all()


class RuleNameParser(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):
        super().__init__(
            option_strings,
            dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: list,
        option_string: str,
    ):
        if values == "-":
            setattr(namespace, "stdin", sys.stdin)
            return
        elif not values:
            if self.nargs == "?" and not namespace.all:
                raise argparse.ArgumentError(self, "Either supply rule ID or use --all")
            return

        match = re.fullmatch(r"(\d{6})(?:\.data)?", values)
        if not match:
            raise argparse.ArgumentError(self, f"Failed to identify rule from argument {values}")
        setattr(namespace, self.dest, match.group(1))


def create_context() -> Context:
    script_directory = os.path.dirname(__file__)
    root_directory = os.path.dirname(os.path.dirname(script_directory))
    return Context(root_directory)


def setup_logger(namespace: argparse.Namespace):
    logger = logging.getLogger()
    logger.setLevel(namespace.log_level)
    logger.addHandler(logging.StreamHandler())


if __name__ == "__main__":
    parser = build_args_parser()
    namespace = parser.parse_args()
    setup_logger(namespace)

    if 'func' in namespace:
        namespace.func(namespace)
    else:
        parser.print_help()
>>>>>>> unified-regex-utils
