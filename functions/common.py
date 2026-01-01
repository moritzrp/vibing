import os


def within_directory(parent_dir: str, target: str) -> bool:
    return os.path.commonpath([parent_dir, target]) == parent_dir


def get_file_paths(working_directory: str, target: str) -> tuple[str, str]:
    wd_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(wd_abs, target))
    return wd_abs, target_dir
