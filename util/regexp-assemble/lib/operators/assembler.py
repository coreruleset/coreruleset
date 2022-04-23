from typing import Iterable, TextIO, List, TypeVar, Generic
from collections.abc import Generator, Iterator

import re, logging, sys

from lib.context import Context
from lib.processors.processor import Processor
from lib.processors.cmdline import CmdLine
from lib.processors.assemble import Assemble

T = TypeVar('T')

class Peekerator(Generic[T]):
    def __init__(self, iterable: Iterable[T]) -> None:
        self.iterator = iter(iterable)
        self.peeked = None

    def __iter__(self) -> Iterator[T]:
        return self.iterator

    def __next__(self) -> T:
        if self.peeked:
            try:
                return self.peeked
            finally:
                self.peeked = None
        else:
            return next(self.iterator)

    def peek(self, default: any=None) -> T:
        if not self.peeked:
            try:
                self.peeked = next(self.iterator)
            except StopIteration:
                return default
        return self.peeked


class Preprocessor(object):
    preprocessor_end_regex = re.compile(r"^##!<.*")

    def __init__(self, peekerator: Peekerator[str], processor_cls: Processor, context: Context, args):
        self.processor = processor_cls.create(context, args)
        # consume the preprocessor comment
        next(peekerator, None)

    def run(self, iterator: Iterator[str]) -> List[str]:
        for line in self._filter(iterator):
            stripped_line = line.rstrip("\n")
            if not stripped_line == "":
                self.processor.process_line(stripped_line)

        return self.processor.complete()

    def _filter(self, iterator: Iterator[str]) -> Generator[str, None, None]:
        line = next(iterator, None)
        while line is not None and not self.preprocessor_end_regex.match(line):
            yield line
            line = next(iterator, None)

class NoOpPreprocessor(object):
    def __init__(self, peekerator: Peekerator[str]) -> None:
        pass

    def run(self, iterator: Iterator[str]) -> List[str]:
        return list(iterator)

class Assembler(object):
    # prefix, suffix, flags, block start block end
    special_comment_markers = '^$+><'
    simple_comment_regex = re.compile(r'^\s*##![^' + special_comment_markers + r'].*')
    preprocessor_regex = re.compile(r'^\s*##!>\s*(.*)')
    logger = logging.getLogger()

    def __init__(self, context: Context):
        self.context = context
        self.preprocessor_map = {
            "cmdline": CmdLine,
            "assemble": Assemble
        }

    def run(self, file: TextIO) -> str:
        peekerator = Peekerator(file.readlines())
        lines = list(self.preprocess(peekerator))
        return self.assemble(lines)

    def detect_preprocessor(self, peekerator: Peekerator[str]) -> Preprocessor:
        match = self.preprocessor_regex.match(peekerator.peek())
        if match is None:
            return NoOpPreprocessor(peekerator)

        definition = match.group(1).split()
        try:
            return self._instantiate_preprocessor(peekerator, definition[0], definition[1:])
        except KeyError:
            self.logger.critical(f"No processor found for {definition}")
            sys.exit(1)

    def _instantiate_preprocessor(self, peekerator: Peekerator[str], name: str, args: List[str]) -> Preprocessor:
        processor_cls = self.preprocessor_map[name]
        return Preprocessor(peekerator, processor_cls, self.context, args)

    def _is_simple_comment(self, line: str) -> bool:
        return self.simple_comment_regex.match(line) is not None

    def preprocess(self, peekerator: Peekerator[str]) -> Peekerator[str]:
        lines: List[str] = []
        while peekerator.peek(None) is not None:
            lines += self._preprocess(peekerator)

        return lines

    

    def assemble(self, lines: List[str]) -> str:
        processor = self._instantiate_preprocessor("assemble", [])
        return processor.run(Peekerator(lines))[0]

    def _preprocess(self, peekerator: Peekerator[str]) -> List[str]:
        processor = self.detect_preprocessor(peekerator)
        lines = self.lines_to_process(peekerator)
        return processor.run(Peekerator(lines))

    def lines_to_process(self, peekerator: Peekerator[str]) -> List[str]:
        start_regex = re.compile(r'^\s*##!>.*')
        end_regex = re.compile(r'^\s*##!<$')
        lines: List[str] = []
        line = peekerator.peek(None)
        while line is not None:
            if end_regex.fullmatch(line):
                # consume the item
                next(peekerator)
                break
            elif start_regex.match(line):
                lines += self._preprocess(peekerator)
            else:
                lines.append(next(peekerator))
            line = peekerator.peek(None)
        return lines
