import uuid
from pathlib import Path
import pytest

from lib.context import Context

@pytest.fixture
def include_file(context, include_file_name):
    file_path = Path.joinpath(context.include_files_directory, include_file_name)
    file_path.touch()
    try:
        yield file_path
    finally:
        file_path.unlink()


@pytest.fixture
def include_file_name():
    return f'{uuid.uuid4()}.data'


@pytest.fixture
def context():
    tests_directory = Path(__file__).parent
    root_directory = tests_directory.parent.parent.parent
    return Context(root_directory)
