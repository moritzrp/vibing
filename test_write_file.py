from typing import NamedTuple

from functions.file_utils import write_file


class TestCase(NamedTuple):
    file: str
    content: str
    working_directory: str = "calculator"


def test(case: TestCase):
    print(f"Result for {case.working_directory}/{case.file}:")
    print(write_file(case.working_directory, case.file, case.content))
    print()


WORKING_DIR = "calculator"

for case in [
    TestCase("lorem.txt", "wait, this isn't lorem ipsum"),
    TestCase("pkg/morelorem.txt", "lorem ipsum dolor sit amet"),
    TestCase("/tmp/temp.txt", "this should not be allowed"),
]:
    test(case)
