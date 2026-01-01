from typing import NamedTuple

from functions.python import run_python_file


class TestCase(NamedTuple):
    wd: str
    file: str
    args: list[str] = []


def test(case: TestCase):
    print(f"Result for {case.wd}/{case.file}:")
    print(run_python_file(case.wd, case.file, case.args))
    print()


for case in [
    TestCase("calculator", "main.py"),
    TestCase("calculator", "main.py", ["3 + 5"]),
    TestCase("calculator", "tests.py"),
    TestCase("calculator", "../main.py"),
    TestCase("calculator", "nonexistent.py"),
    TestCase("calculator", "lorem.txt"),
]:
    test(case)
