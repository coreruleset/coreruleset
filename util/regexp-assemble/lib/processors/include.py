from pathlib import Path
from typing import TypeVar, List

from lib.processors.processor import Processor
from lib.context import Context

T = TypeVar("T", bound="Include")


class Include(Processor):
    def __init__(self, context: Context, file_path: Path):
        super().__init__(context)

        self.file_path = file_path

    # override
    @classmethod
    def create(cls: T, context: Context, args: List[str]) -> T:
        if len(args) < 1:
            raise ValueError('No file name supplied to include processor')

        file_name = str(Path(args[0]).stem)
        for file in context.include_files_directory.iterdir():
            if file.stem == file_name:
                return cls(context, file)

        raise ValueError(f'Include file {file_name} not found')


    # override
    def has_body(self):
        return False

    # override
    def process_line(self, _):
        raise ValueError('Include processor does not support line processing')

    # override
    def complete(self) -> List[str]:
        self.logger.debug('Completing include processor')
        with self.file_path.open('rt') as handle:
            return handle.readlines()
