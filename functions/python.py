import os
import subprocess

from google.genai import types

from functions.common import get_file_paths, within_directory

SCHEMA_RUN_PYTHON_FILE = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a python file in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the python file to execute. Relative to the working directory (default is the working directory itself)",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Argument to pass to the python file on execution.",
                ),
            ),
        },
    ),
)


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
):
    try:
        wd_abs, target_file = get_file_paths(working_directory, file_path)

        if not within_directory(wd_abs, target_file):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if os.path.splitext(target_file)[-1] != ".py":
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_file]
        if args:
            command.extend(args)

        result = subprocess.run(
            command, cwd=wd_abs, capture_output=True, text=True, timeout=30.0
        )

        message = ""
        if result.returncode != 0:
            message += f"Process exited with code {result.returncode}"
        if len(result.stderr) == 0 and len(result.stdout) == 0:
            message += "No output produced"
        else:
            message += f"STDOUT: {result.stdout}"
            message += f"STDERR: {result.stderr}"
        return message
    except Exception as e:
        return f"Error: executing python file: {e}"
