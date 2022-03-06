#! /usr/bin/env python

# This script is a simple wrapper around regexp-assemble.pl, regexp-cmdline.py, and
# regexp-negativelookbehind.py. It takes a rule id, data file name or data file path
# as input and runs it through the scripts, depending on the marker flags present in
# the data file. The last step is to always run the output through regexp-assemble.pl.
#
# Preprocessors are defined in this file. To add a new preprocessor, add an entry to
# the preprocessor_map. The key of the entry is the keyword used in the data file
# and the value is the script you want to execute (expected to be in the lib directory).

import os, re, sys
from pydoc import cram
import argparse
from lib.operators.assembler import Assembler
from lib.operators.comparer import Comparer
from lib.operators.updater import Updater
from lib.context import Context


def build_args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Utilities for generating and managing regular expressions in CRS rule files"
    )
    subparsers = parser.add_subparsers()
    build_generate_args_parser(subparsers)
    build_update_args_parser(subparsers)
    build_compare_args_parser(subparsers)

    return parser


def build_generate_args_parser(subparsers):
    parser = subparsers.add_parser("generate")
    parser.add_argument("rule_id", action=RuleNameParser)
    parser.set_defaults(func=handle_generate)


def build_update_args_parser(subparsers):
    parser = subparsers.add_parser("update")
    parser.add_argument("rule_id", nargs="?", action=RuleNameParser, default=None)
    parser.add_argument("--all", action="store_true")
    parser.set_defaults(func=handle_update)


def build_compare_args_parser(subparsers):
    parser = subparsers.add_parser("compare")
    parser.add_argument("rule_id", nargs="?", action=RuleNameParser, default=None)
    parser.add_argument("--all", action="store_true")
    parser.set_defaults(func=handle_compare)


def handle_generate(namespace: argparse.Namespace):
    context = create_context()
    assembler = Assembler(context)

    if namespace.rule_id:
        with open(
            os.path.join(context.data_files_directory, f"{namespace.rule_id}.data")
        ) as handle:
            lines = assembler.run(handle)
    elif "stdin" in namespace:
        lines = assembler.run(namespace.stdin)
    else:
        raise argparse.ArgumentError("Unhandled combination of arguments")

    for index, line in enumerate(lines):
        sys.stdout.write(line.decode('utf-8'))
        if index + 1 < len(lines):
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
    def __init__(self, option_strings, dest, nargs=None, default=None, required=False):
        super().__init__(
            option_strings, dest, nargs=nargs, default=default, required=required
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
                raise ValueError("Invalid arguments")
            return

        match = re.fullmatch(r"(\d{6})(?:\.data)?", values)
        if not match:
            raise ValueError(f"Failed to identify rule from argument {values}")
        setattr(namespace, self.dest, match.group(1))

def create_context() -> Context:
    script_directory = os.path.dirname(__file__)
    root_directory = os.path.dirname(os.path.dirname(script_directory))
    return Context(root_directory)

if __name__ == "__main__":
    namespace = build_args_parser().parse_args()
    namespace.func(namespace)
