#! /usr/bin/env python3

# This script is a simple wrapper around regexp-assemble.pl, regexp-cmdline.py, and
# regexp-negativelookbehind.py. It takes a rule id, data file name or data file path
# as input and runs it through the scripts, depending on the marker flags present in
# the data file. The last step is to always run the output through regexp-assemble.pl.
#
# Preprocessors are defined in this file. To add a new preprocessor, add an entry to
# the preprocessor_map. The key of the entry is the keyword used in the data file
# and the value is the script you want to execute (expected to be in the lib directory).

import re, sys
import argparse
import logging
from pathlib import Path
from typing import TypeVar

from lib.operators.assembler import Assembler
from lib.operators.comparer import Comparer
from lib.operators.updater import Updater
from lib.context import Context

S = TypeVar("S", bound="argparse._SubParserAction[argparse.ArgumentParser]")


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
    The ID of the rule, e.g., 932100, or the data file name.
    The special token `-` will cause the script to accept input
    from stdin.
    """,
    )
    parser.set_defaults(func=handle_generate)


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
        help="The ID of the rule, e.g., 932100, or the data file name",
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
        help="The ID of the rule, e.g., 932100, or the data file name",
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


def handle_generate(namespace: argparse.Namespace):
    context = create_context(namespace)
    assembler = Assembler(context)

    if namespace.rule_id:
        with (context.data_files_directory / namespace.fileName).open("rt") as handle:
            regex = assembler.run(handle)
    elif "stdin" in namespace:
        regex = assembler.run(namespace.stdin)
    else:
        raise argparse.ValueError("Unhandled combination of arguments")

    sys.stdout.write(regex)
    sys.stdout.write("\n")


def handle_update(namespace: argparse.Namespace):
    updater = Updater(create_context(namespace))
    if namespace.rule_id:
        updater.run(False)
    elif namespace.all:
        updater.run(True)


def handle_compare(namespace: argparse.Namespace):
    comparer = Comparer(create_context(namespace))
    if namespace.rule_id:
        comparer.run(False)
    elif namespace.all:
        comparer.run(True)


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

        match = re.fullmatch(r"(\d{6})(?:-chain(\d+))?(?:\.data)?", values)
        if not match:
            raise argparse.ArgumentError(self, f"Failed to identify rule from argument {values}")
        setattr(namespace, self.dest, match.group(1))
        setattr(namespace, "chain_offset", int(match.group(2) if match.group(2) else 0))
        setattr(namespace, "fileName", values + ".data")


def create_context(namespace: argparse.Namespace) -> Context:
    script_directory = Path(__file__).parent
    root_directory = Path(script_directory).parent.parent
    return Context(root_directory, namespace)


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
