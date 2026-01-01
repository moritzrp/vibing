from typing import NamedTuple

from functions.file_utils import get_file_content


class TestCase(NamedTuple):
    working_directory: str
    file: str


def test(case: TestCase):
    print(f"Result for {case.working_directory} / {case.file}:")
    print(get_file_content(case.working_directory, case.file))
    print()


print(get_file_content("data", "loremipsum.txt"))
for case in [
    TestCase("data", "loremipsum.txt"),
    TestCase("calculator", "main.py"),
    TestCase("calculator", "pkg/calculator.py"),
    TestCase("calculator", "/bin/cat"),
    TestCase("calculator", "pkg/does_not_exist.py"),
]:
    test(case)
