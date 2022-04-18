from typing import TypeVar

from subprocess import Popen, PIPE, TimeoutExpired
import sys

from lib.processors.processor import Processor
from lib.context import Context

T = TypeVar("T", bound="Assemble")


class Assemble(Processor):
    def __init__(self, context: Context):
        super().__init__()

        self.context = context

    # override
    @classmethod
    def create(cls: T, context: Context, args: list[str]) -> T:
        # TODO:
        # - handle prefix / suffix -> what are the cases? alternation, prefix, suffix? generalizeable?
        # - call preprocess() recursively to support nesting (from inner most to outer most)
        # - handle data split accross multiple files
        # - add tests!
        return cls(context)

    # override
    def process_line(self, line: str):
        self.lines.append(line)

    # override
    def complete(self) -> list[str]:
        try:
            args = [self.context.regexp_assemble_pl_path]
            outs = None
            errs = None
            proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            for line in self.lines:
                proc.stdin.write(line.encode("utf-8"))
                proc.stdin.write(b"\n")
            try:
                outs, errs = proc.communicate(timeout=30)
            except TimeoutExpired:
                proc.kill()
                self.logger.error("Assembling regex timed out")
                self.logger.err("Stderr: %s", errs)
                sys.exit(1)

            if errs:
                self.logger.error("Failed to assemble regex")
                self.logger.error("Stderr: %s", errs)
                sys.exit(1)

            return [outs.split(b"\n")[0].decode("utf-8")]
        finally:
            self.lines = []
