import os


class Context(object):
    def __init__(self, root_directory: str):
        self.root_directory = root_directory
        self.rules_directory = os.path.join(self.root_directory, "rules")
        self.util_directory = os.path.join(self.root_directory, "util")
        self.regexp_assemble_directory = os.path.join(
            self.util_directory, "regexp-assemble"
        )
        self.data_files_directory = os.path.join(self.regexp_assemble_directory, "data")
        self.regexp_assemble_pl_path = os.path.join(
            self.regexp_assemble_directory, "lib", "regexp-assemble.pl"
        )

        assert (
            os.path.exists(self.rules_directory)
            and os.path.exists(self.util_directory)
            and os.path.exists(self.regexp_assemble_directory)
            and os.path.exists(self.data_files_directory)
        )
