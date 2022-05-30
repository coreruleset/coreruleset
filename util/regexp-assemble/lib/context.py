import argparse
from pathlib import Path


class Context(object):
    def __init__(self, root_directory: Path, namespace: argparse.Namespace=None):
        self.root_directory = root_directory
        self.rules_directory = self.root_directory / "rules"
        self.util_directory = self.root_directory / "util"
        self.regexp_assemble_directory = self.util_directory / "regexp-assemble"
        self.data_files_directory = self.regexp_assemble_directory / "data"
        self.include_files_directory = self.regexp_assemble_directory / "data" / "include"
        self.regexp_assemble_pl_path = self.regexp_assemble_directory / "lib" / "regexp-assemble.pl"
        self.single_rule_id = namespace.rule_id if namespace else None
        self.single_chain_offset = None
        if namespace and "chain_offset" in namespace:
            self.single_chain_offset = namespace.chain_offset

        assert (
            self.rules_directory.exists()
            and self.util_directory.exists()
            and self.regexp_assemble_directory.exists()
            and self.data_files_directory.exists()
            and self.include_files_directory.exists()
        )
