from msc_pyparser import MSCWriter
from lib.operators.parser import Parser


class Updater(Parser):
    def run(self, process_all: bool):
        self.perform_compare_or_update(process_all, self.update_regex)
        self.write_updates()

    def update_regex(
        self,
        rule_id: str,
        generated_regex: str,
        current_regex: str,
        config: dict,
        config_key: str,
    ):
        config[config_key] = generated_regex

    def write_updates(self):
        for rule_prefix, parser in self.parsers.items():
            writer = MSCWriter(parser.configlines)
            with self.prefix_to_file_map[rule_prefix].open("w") as handle:
                writer.generate()
                # add extra new line at the end of file
                writer.output.append("")
                handle.write("\n".join(writer.output))
