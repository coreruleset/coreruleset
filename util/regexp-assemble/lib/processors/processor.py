from abc import abstractmethod

from abc import ABC
from typing import TypeVar, Type

T = TypeVar('T', bound='Processor')
class Processor(ABC):
    @classmethod
    @abstractmethod
    def create(cls: Type[T]) -> T:
        pass

    @abstractmethod
    def process_line(self, line: bytes):
        pass

    @abstractmethod
    def complete(self) -> bytes:
        pass
