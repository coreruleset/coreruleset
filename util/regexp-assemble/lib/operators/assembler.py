from typing import Iterable, TextIO, List, TypeVar, Generic, Generator, Iterator

import re, logging, sys

from lib.context import Context
from lib.processors.processor import Processor
from lib.processors.cmdline import CmdLine
from lib.processors.assemble import Assemble
from lib.processors.template import Template
from lib.processors.include import Include

T = TypeVar('T')

COMMENT_REGEX_PREFIX = r'\s*##!'
# prefix, suffix, flags, block start block end
SPECIAL_COMMENT_MARKERS = '^$+><='
PREPROCESSOR_START_REGEX = re.compile(rf'{COMMENT_REGEX_PREFIX}>\s*(.*)')
PREPROCESSOR_END_REGEX = re.compile(rf'{COMMENT_REGEX_PREFIX}<')
SIMPLE_COMMENT_REGEX = re.compile(rf'{COMMENT_REGEX_PREFIX}[^{SPECIAL_COMMENT_MARKERS}]')

class NestingError(Exception):
    def __init__(self, line: int, depth: int):
        super().__init__(f"Nesting error on line {line}, nesting level {depth}")

        self.line = line
        self.depth = depth

class Stats(object):
    def __init__(self):
        self.line = 0
        self.depth = 0

    def line_parsed(self):
        self.line += 1

    def processor_start(self):
        self.depth += 1

    def processor_end(self):
        self.depth -= 1
        if self.depth < 0:
            raise NestingError(self.line, self.depth)

class Peekerator(Generic[T]):
    def __init__(self, iterable: Iterable[T]) -> None:
        self.iterator = iter(iterable)
        self.peeked = None

    def __iter__(self) -> Iterator[T]:
        return self.iterator

    def __next__(self) -> T:
        if self.peeked is not None:
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
    def __init__(self, peekerator: Peekerator[str], processor_cls: Processor, context: Context, args):
        self.processor = processor_cls.create(context, args)
        if PREPROCESSOR_START_REGEX.match(peekerator.peek('')):
            # when instantiated programmatically, the preprocessor marker won't be there
            # consume the preprocessor comment
            next(peekerator, None)

    def run(self, peekerator: Peekerator[str]) -> List[str]:
        for line in self._filter(peekerator):
            stripped_line = line.rstrip("\n")
            if not stripped_line == '':
                self.processor.process_line(stripped_line)

        return self.processor.complete()

    def has_body(self):
        return self.processor.has_body()

    def _filter(self, peekerator: Peekerator[str]) -> Generator[str, None, None]:
        line = next(peekerator, None)
        while line is not None and not PREPROCESSOR_END_REGEX.match(line):
            yield line
            line = next(peekerator, None)

class NoOpPreprocessor(object):
    def __init__(self, peekerator: Peekerator[str]) -> None:
        self.processor = None
        pass

    def run(self, iterator: Iterator[str]) -> List[str]:
        return list(iterator)

    def has_body(self):
        return True

class Assembler(object):
    logger = logging.getLogger()

    def __init__(self, context: Context):
        self.context = context
        self.stats = Stats()
        self.preprocessor_map = {
            "cmdline": CmdLine,
            "assemble": Assemble,
            "template": Template,
            "include": Include
        }

    def run(self, file: TextIO) -> str:
        peekerator = Peekerator(file.readlines())
        return self._run(peekerator)

    def _run(self, peekerator: Peekerator) -> str:
        lines = list(self.preprocess(peekerator))
        self.logger.debug('preprocessed lines: %s', lines)
        return self.assemble(lines)

    def detect_preprocessor(self, peekerator: Peekerator[str]) -> Preprocessor:
        match = PREPROCESSOR_START_REGEX.match(peekerator.peek())
        if match is None:
            return NoOpPreprocessor(peekerator)

        self.stats.processor_start()
        definition = match.group(1).split()
        try:
            return self._instantiate_preprocessor(peekerator, definition[0], definition[1:])
        except KeyError:
            self.logger.critical('No processor found for %s', definition)
            sys.exit(1)

    def _instantiate_preprocessor(self, peekerator: Peekerator[str], name: str, args: List[str]) -> Preprocessor:
        processor_cls = self.preprocessor_map[name]
        return Preprocessor(peekerator, processor_cls, self.context, args)

    def _is_simple_comment(self, line: str) -> bool:
        return SIMPLE_COMMENT_REGEX.match(line) is not None

    def preprocess(self, peekerator: Peekerator[str]) -> Peekerator[str]:
        lines: List[str] = []
        while peekerator.peek() is not None:
            lines += self._preprocess(peekerator)

        # the outermost preprocessor end marker is optional
        if self.stats.depth > 1:
            raise NestingError(self.stats.line, self.stats.depth)

        return lines

    def assemble(self, lines: List[str]) -> str:
        peekerator = Peekerator(lines)
        processor = self._instantiate_preprocessor(peekerator, "assemble", [])
        result = processor.run(peekerator)
        return result[0] if len(result) > 0 else ''

    def _preprocess(self, peekerator: Peekerator[str]) -> List[str]:
        processor = self.detect_preprocessor(peekerator)
        self.logger.debug('detected processor: %s', processor.processor.__class__)
        lines = self.lines_to_process(peekerator, processor)
        self.logger.debug('processor will process: %s', lines)
        return processor.run(Peekerator(lines))

    def lines_to_process(self, peekerator: Peekerator[str], processor: Preprocessor) -> List[str]:
        lines: List[str] = [] 
        line = peekerator.peek()
        while line is not None:
            self.stats.line_parsed()

            if PREPROCESSOR_END_REGEX.match(line):
                # consume the item
                next(peekerator)
                self.stats.processor_end()
                self.logger.debug('Found preprocessor end marker')
                break
            elif not processor.has_body():
                self.stats.processor_end()
                self.logger.debug('Preprocessor has no body. No lines to process')
                break
            elif line.strip() == '' or SIMPLE_COMMENT_REGEX.match(line):
                # consume the item
                next(peekerator)
                self.logger.debug('Found simple comment')
            elif PREPROCESSOR_START_REGEX.match(line):
                lines += self._preprocess(peekerator)
                self.logger.debug('Found preprocessor start marker')
            else:
                lines.append(next(peekerator))
                self.logger.debug('Found regular input %r', line)
            line = peekerator.peek()
        return lines
