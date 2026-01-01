import os

from google.genai import types

from config import MAX_CHARS
from functions.common import get_file_paths, within_directory

SCHEMA_GET_FILES_INFO = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            )
        },
    ),
)

SCHEMA_GET_FILE_CONTENT = types.FunctionDeclaration(
    name="get_file_content",
    description="Get the content of a file in a specified directory relative to the working directory. Content above a threshold is truncated",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to read. Relative to the working directory (default is the working directory itself)",
            )
        },
    ),
)

SCHEMA_WRITE_FILE = types.FunctionDeclaration(
    name="write_file",
    description="Write content to a file in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write. Relative to the working directory (default is the working directory itself)",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
    ),
)


def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        wd_abs, target_dir = get_file_paths(working_directory, directory)

        if not os.path.isdir(target_dir):
            return f'Error: "{target_dir}" is not a directory'

        if not within_directory(wd_abs, target_dir):
            return f"Error: Cannot list '{target_dir}' as it is outside the permitted working directory."

        contents: list[str] = []
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            contents.append(
                f"- {item}: file_size={os.path.getsize(item_path)}, is_dir={os.path.isdir(item_path)}"
            )
        return "\n".join(contents)
    except Exception as e:
        return f"Error: {e.__str__()}"


def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        wd_abs, target_file = get_file_paths(working_directory, file_path)

        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        if not within_directory(wd_abs, target_file):
            return f"Error: Cannot read '{target_file}' as it is outside the permitted working directory."

        with open(target_file, "r") as f:
            content = f.read(MAX_CHARS)
            if f.read(1):
                content += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
                )
        return content
    except Exception as e:
        return f"Error: {e.__str__()}"


def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        wd_abs, target_file = get_file_paths(working_directory, file_path)

        if not within_directory(wd_abs, target_file):
            return f"Error: Cannot read '{target_file}' as it is outside the permitted working directory."

        if os.path.isdir(target_file):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        with open(target_file, "w") as f:
            n_lines = f.write(content)

        return f'Successfully wrote to "{file_path}" ({n_lines} characters written)'
    except Exception as e:
        return f"Error: {e.__str__()}"
