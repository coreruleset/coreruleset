from typing import TypeVar, List

import re

from lib.processors.processor import Processor
from lib.context import Context

T = TypeVar("T", bound="Template")


class Template(Processor):
    identifier_pattern = r'[a-zA-Z\d_-]+'
    identifier_regex = re.compile(rf'^{identifier_pattern}$')
    template_regex = re.compile(rf'{{{{({identifier_pattern})}}}}')

    def __init__(self, context: Context, identifier: str, replacement: str):
        super().__init__(context)

        self.identifier = identifier
        self.replacement = replacement

    # override
    @classmethod
    def create(cls: T, context: Context, args: List[str]) -> T:
        if len(args) < 1:
            raise ValueError('No identifier supplied to template processor')
        if len(args) < 2:
            raise ValueError('No replacement supplied to template processor')


        identifier = args[0]
        if not cls.identifier_regex.match(identifier):
            raise ValueError('Invalid identifier format. Only ASCII characters and numbers allowed')

        return cls(context, identifier, args[1])

    # override
    def process_line(self, line: str):
        match = self.template_regex.search(line)
        if match and match.group(1) == self.identifier:
            self.logger.debug('Found template %s in line %s', self.identifier, line)
            # need to use a function as the replacement to prevent Python from parsing
            # escape sequences
            transformed_line = self.template_regex.sub(lambda _: self.replacement, line)
            self.lines.append(transformed_line)
            self.logger.debug('Transformed line: %s', transformed_line)
        else:
            self.lines.append(line)

    # override
    def complete(self) -> List[str]:
        self.logger.debug('Completing template processor')
        return self.lines
