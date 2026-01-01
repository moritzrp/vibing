from google.genai import types

from functions import file_utils, python

AVAILABLE_FUNCTIONS = types.ToolListUnion(
    [
        types.Tool(
            function_declarations=[
                file_utils.SCHEMA_GET_FILES_INFO,
                file_utils.SCHEMA_GET_FILE_CONTENT,
                file_utils.SCHEMA_WRITE_FILE,
                python.SCHEMA_RUN_PYTHON_FILE,
            ]
        )
    ]
)

FUNCTION_MAP = {
    "get_file_content": file_utils.get_file_content,
    "get_files_info": file_utils.get_files_info,
    "write_file": file_utils.write_file,
    "run_python_file": python.run_python_file,
}


def call_function(function_call: types.FunctionCall, verbose: bool = False):
    function_name = function_call.name or ""
    if not function_name:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    args = dict(function_call.args) if function_call.args else {}
    args["working_directory"] = "./calculator"
    result = FUNCTION_MAP[function_name](**args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name, response={"result": result}
            )
        ],
    )
