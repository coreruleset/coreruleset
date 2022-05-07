import sys
from math import ceil

from lib.operators.parser import Parser


class Comparer(Parser):
    def run(self, process_all: bool):
        self.perform_compare_or_update(process_all, self.compare_regex)

    def compare_regex(
        self,
        rule_id: str,
        generated_regex: str,
        current_regex: str,
        config: dict,
        config_key: str,
    ):
        if current_regex == generated_regex:
            sys.stdout.write(f"Regex of {rule_id} has not changed\n")
        else:
            sys.stdout.write(f"Regex of {rule_id} has changed!\n")
            diff_found = False
            max_chunks = ceil(max(len(current_regex), len(generated_regex)) / 50)
            for index in range(0, max_chunks * 50, 50):
                end_index = min(len(current_regex), index + 50)
                if end_index > index:
                    current_chunk = current_regex[index:end_index]
                end_index = min(len(generated_regex), index + 50)
                if end_index > index:
                    generated_chunk = generated_regex[index:end_index]

                print_first_diff = (
                    not diff_found
                    and current_chunk
                    and generated_chunk
                    and current_chunk != generated_chunk
                )
                if print_first_diff:
                    diff_found = True
                    sys.stdout.write("\n===========\nfirst difference\n-----------")
                if current_chunk:
                    sys.stdout.write("\ncurrent:  ")
                    sys.stdout.write(current_chunk.rjust(len(current_chunk) + 5))
                    counter = f"({int(index / 50) + 1} / {ceil(len(current_regex) / 50)})"
                    if generated_chunk is None or current_chunk != generated_chunk:
                        counter = "~ " + counter
                    sys.stdout.write(counter.rjust(65 - len(current_chunk)))
                if generated_chunk:
                    sys.stdout.write("\ngenerated: ")
                    sys.stdout.write(generated_chunk.rjust(len(generated_chunk) + 4))
                    counter = f"({int(index / 50) + 1} / {ceil(len(current_regex) / 50)})"
                    if current_chunk is None or current_chunk != generated_chunk:
                        counter = "~ " + counter
                    sys.stdout.write(counter.rjust(65 - len(generated_chunk)))
                    sys.stdout.write("\n")
                if print_first_diff:
                    sys.stdout.write("===========\n")

            sys.stdout.write("\n")
