from abc import abstractmethod
from abc import ABC
from typing import TypeVar, List

import re
import logging

from lib.context import Context

T = TypeVar("T", bound="Processor")

class Processor(ABC):
    comment_regex = re.compile(r"^##!")
    logger = logging.getLogger()

    def __init__(self, context: Context):
        self.lines: List[str] = []
        self.context = context

    @classmethod
    @abstractmethod
    def create(cls: T, context: Context, args: List[str]) -> T:
        pass

    def has_body(self):
        return True

    @abstractmethod
    def process_line(self, line: str):
        pass

    @abstractmethod
    def complete(self) -> List[str]:
        pass
