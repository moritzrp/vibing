from typing import NamedTuple
from functions.file_utils import get_files_info


class Section(NamedTuple):
    title: str
    target: str


def test_section(section: Section):
    print(f"Result for {section.title} directory:")
    print(get_files_info("calculator", section.target))
    print()


for section in [
    Section("current", "."),
    Section("pkg", "pkg"),
    Section("/bin", "/bin"),
    Section("../", "../"),
]:
    test_section(section)
