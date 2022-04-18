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

    def __init__(self):
        self.lines: List[str] = []

    @classmethod
    @abstractmethod
    def create(cls: T, context: Context, args: List[str]) -> T:
        pass

    @abstractmethod
    def process_line(self, line: str):
        pass

    @abstractmethod
    def complete(self) -> list[str]:
        pass
