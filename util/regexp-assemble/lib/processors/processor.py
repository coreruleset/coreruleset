from abc import abstractmethod
from abc import ABC
from typing import TypeVar, Type

import re
import logging

T = TypeVar("T", bound="Processor")

class Processor(ABC):
    comment_regex = re.compile(r"^##!")
    logger = logging.getLogger()

    @classmethod
    @abstractmethod
    def create(cls: T) -> T:
        pass

    @abstractmethod
    def process_line(self, line: bytes):
        pass

    @abstractmethod
    def complete(self) -> bytes:
        pass
