from typing import TypeVar

from subprocess import Popen, PIPE, TimeoutExpired
import sys, re

from lib.processors.processor import Processor
from lib.context import Context

T = TypeVar("T", bound="Assemble")


class Assemble(Processor):
    def __init__(self, context: Context):
        super().__init__(context)

    # override
    @classmethod
    def create(cls: T, context: Context, args: list[str]) -> T:
        if len(args) == 0:
            return cls(context)

        type = args[0]
        if type == 'concat':
            return AssembleConcat(context)
        else:
            raise ValueError(f'No assemble processor of type {type} known')

    # override
    def process_line(self, line: str):
        self.lines.append(line)

    # override
    def complete(self) -> list[str]:
        self.logger.debug('assembling lines: %s', self.lines)
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

            output = [outs.split(b"\n")[0].decode("utf-8")]
            self.logger.debug('completed assembly: %s', output[0])
            return output
        finally:
            self.lines = []


class AssembleConcat(Assemble):
    input_regex = re.compile(r'^\s*##!=<\s*(.*)$')
    output_regex = re.compile(r'^\s*##!=>\s*(.*)$')
    stash = {}

    def __init__(self, context: Context):
        super().__init__(context)

        self.output = ''

    def process_line(self, line: str):
        match = self.input_regex.match(line)
        if match:
            self._store(match.group(1))
            return

        match = self.output_regex.match(line)
        if match:
            self._append(match.group(1))
        else: 
            super().process_line(line)

    def complete(self):
        result = self.output + super().complete()[0]
        if result == '':
            return []
        else:
            return [result]

    def _store(self, identifier: str):
        if not identifier:
            raise ValueError('missing identifier for input marker')

        self.stash[identifier] = super().complete()[0]

    def _append(self, identifier:str):
        if not identifier:
            self.output += super().complete()[0]
        else:
            self.output += self.stash[identifier]
