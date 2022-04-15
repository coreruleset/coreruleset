import re, sys
from subprocess import Popen, PIPE, TimeoutExpired
from typing import TextIO, List
import logging

from lib.context import Context
from lib.processors.processor import Processor
from lib.processors.cmdline import CmdLine


class Preprocessor(object):
    def __init__(self, processor_cls: Processor, args):
        self.processor = processor_cls.create(*args)

    def run(self, iterator):
        return self._preprocess(iterator, self._filter)

    def _preprocess(self, iterator, filter):
        for line in filter(iterator):
            stripped_line = line.rstrip("\n")
            if not stripped_line == "":
                self.processor.process_line(stripped_line)

        return self.processor.complete()


class FilePreprocessor(Preprocessor):
    def _filter(self, iterator):
        for line in iterator:
            yield line


class LinePreprocessor(Preprocessor):
    def _filter(self, iterator):
        yield next(iterator)


class BlockPreprocessor(Preprocessor):
    block_preprocessor_end_regex = re.compile(r"^##!<.*")

    def _filter(self, iterator):
        line = next(iterator, None)
        while line is not None and not self.block_preprocessor_end_regex.match(line):
            yield line
            line = next(iterator, None)


class Assembler(object):
    special_comment_markers = "^$+><"
    simple_comment_regex = re.compile(r"^##![^" + special_comment_markers + r"].*")
    # prefix, suffix, flags, block start block end
    preprocessor_regex = re.compile(r"^##!>\s*(.*)")
    logger = logging.getLogger()

    def __init__(self, context: Context):
        self.context = context
        self.preprocessor_map = {
            "cmdline": (FilePreprocessor, CmdLine),
        }

    def run(self, file: TextIO) -> str:
        iterator = file.readlines().__iter__()
        lines = self.preprocess(iterator)
        return self.assemble(lines)

    def detect_preprocessor(self, line: str) -> Preprocessor:
        match = self.preprocessor_regex.match(line)
        if match is None:
            return

        definition = match.group(1).split()
        try:
            processor_type, processor_cls = self.preprocessor_map[definition[0]]
            return processor_type(processor_cls, definition[1:])
        except KeyError:
            self.logger.critical(f"No processor found for {definition}")
            sys.exit(1)

    def _is_simple_comment(self, line: str) -> bool:
        return self.simple_comment_regex.match(line) is not None

    def preprocess(self, lines: List[str]) -> List[str]:
        iterator = lines.__iter__()
        final_lines = []
        for processor_type in (LinePreprocessor, BlockPreprocessor, FilePreprocessor):
            transformed_lines = []
            line = next(iterator, None)
            while line is not None:
                if self._is_simple_comment(line):
                    line = next(iterator, None)
                    continue
                processor = self.detect_preprocessor(line)
                if processor is None or not isinstance(processor, processor_type):
                    transformed_lines.append(line)
                    line = next(iterator, None)
                    continue
                transformed_lines += processor.run(iterator)
                line = next(iterator, None)

            final_lines = transformed_lines
            iterator = final_lines.__iter__()
        return final_lines

    def assemble(self, lines: List[str]) -> str:
        args = [self.context.regexp_assemble_pl_path]
        outs = None
        errs = None
        proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for line in lines:
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

        return outs.split(b"\n")[0].decode("utf-8")
