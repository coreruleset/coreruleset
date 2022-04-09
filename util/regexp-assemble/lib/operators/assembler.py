from typing import TextIO
from collections.abc import Generator, Iterator

import re, logging, sys

from lib.context import Context
from lib.processors.processor import Processor
from lib.processors.cmdline import CmdLine
from lib.processors.assemble import Assemble


class Preprocessor(object):
    def __init__(self, processor_cls: Processor, context: Context, args):
        self.processor = processor_cls.create(context, args)

    def run(self, iterator: Iterator[str]) -> list[str]:
        return self._preprocess(iterator, self._filter)

    def _preprocess(self, iterator: Iterator[str], filter) -> list[str]:
        for line in filter(iterator):
            stripped_line = line.rstrip("\n")
            if not stripped_line == "":
                self.processor.process_line(stripped_line)

        return self.processor.complete()

    def _filter(self, iterator: Iterator[str]) -> Generator[str, None, None]:
        for line in iterator:
            yield line


class FilePreprocessor(Preprocessor):
    pass


class LinePreprocessor(Preprocessor):
    # override
    def _filter(self, iterator):
        yield next(iterator)


class BlockPreprocessor(Preprocessor):
    block_preprocessor_end_regex = re.compile(r"^##!<.*")

    # override
    def _filter(self, iterator: Iterator[str]) -> Generator[str, None, None]:
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
            "cmdline": (BlockPreprocessor, CmdLine),
            "assemble": (BlockPreprocessor, Assemble)
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
            return self._instantiate_preprocessor(definition[0], definition[1:])
        except KeyError:
            self.logger.critical(f"No processor found for {definition}")
            sys.exit(1)

    def _instantiate_preprocessor(self, name: str, args: list[str]) -> Preprocessor:
        processor_type, processor_cls = self.preprocessor_map[name]
        return processor_type(processor_cls, self.context, args)

    def _is_simple_comment(self, line: str) -> bool:
        return self.simple_comment_regex.match(line) is not None

    def preprocess(self, iterator: Iterator[str]) -> list[str]:
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

    def assemble(self, lines: list[str]) -> str:
        processor = self._instantiate_preprocessor("assemble", [])
        return processor.run(lines.__iter__())[0]
