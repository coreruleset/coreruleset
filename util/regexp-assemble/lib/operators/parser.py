import re, os
from typing import Mapping
import logging

from msc_pyparser import MSCParser
from lib.context import Context
from lib.operators.assembler import Assembler


class Parser(object):
    rule_id_regex = re.compile(r"^(\d{6})")
    parsers: Mapping[str, MSCParser] = {}
    prefix_to_file_map: Mapping[str, str] = {}
    logger = logging.getLogger()

    def __init__(self, context: Context):
        self.context = context

    def perform_compare_or_update(self, rule_id: str = None, func=None):
        files = os.listdir(self.context.data_files_directory)
        files.sort()
        assembler = Assembler(self.context)
        if rule_id:
            for file in files:
                if rule_id in file:
                    self.process_regex(
                        os.path.join(self.context.data_files_directory, file),
                        assembler,
                        func,
                    )
                    break
        else:
            for file in files:
                self.process_regex(
                    os.path.join(self.context.data_files_directory, file),
                    assembler,
                    func,
                )

    def process_regex(self, file_path: str, assembler: Assembler, func):
        rule_id = self.rule_id_regex.match(os.path.basename(file_path)).group(1)
        with open(file_path, "rt") as file:
            regex = assembler.run(file)

        self.logger.info("Processing %s", rule_id)
        rule_prefix = rule_id[:3]
        if rule_prefix in self.parsers:
            parser = self.parsers[rule_prefix]
        else:
            for rule_file in os.listdir(self.context.rules_directory):
                if rule_prefix in rule_file:
                    self.prefix_to_file_map[rule_prefix] = rule_file
                    with open(
                        os.path.join(self.context.rules_directory, rule_file), "rt"
                    ) as handle:
                        parser = MSCParser()
                        self.parsers[rule_prefix] = parser
                        parser.parser.parse(handle.read())
                        break
            if not parser:
                raise Warning(f"No rule file found for data file {file}")

        for config in parser.configlines:
            if config["type"] == "SecRule":
                for action in config["actions"]:
                    if action["act_name"] == "id" and action["act_arg"] == rule_id:
                        func(
                            rule_id,
                            regex,
                            config["operator_argument"],
                            config,
                            "operator_argument",
                        )
                        break
