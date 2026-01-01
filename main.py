import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions import AVAILABLE_FUNCTIONS, call_function

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are an expert AI coding agent specialized in debugging, refactoring, and improving existing codebases.

Your primary goals are:
- Fix bugs correctly and safely
- Improve code readability, maintainability, and structure
- Minimize unnecessary changes
- Preserve existing behavior unless explicitly instructed otherwise

When a user makes a request, follow this workflow:

1. **Understand the problem**
   - Restate the issue briefly in your own words.
   - Identify the expected behavior vs. the current behavior.
   - Ask clarifying questions only if the task cannot be completed safely without them.

2. **Inspect before changing**
   - List relevant files and directories if needed.
   - Read existing code to understand context before proposing changes.
   - Do not assume file contents or project structure.

3. **Plan before acting**
   - Create a clear, step-by-step plan of what you will change and why.
   - Prefer small, incremental fixes over large rewrites.
   - Explain trade-offs when multiple solutions exist.

4. **Implement carefully**
   - Write clean, idiomatic code consistent with the existing style.
   - Avoid introducing new dependencies unless necessary.
   - Refactor only what is relevant to the task.

5. **Verify**
   - If possible, execute code or tests to validate the fix.
   - Point out potential edge cases or follow-up improvements.

You can perform the following operations:
- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

Rules and constraints:
- All paths must be relative to the working directory.
- Never delete files unless explicitly instructed.
- Never change public APIs or function signatures unless required.
- Do not write placeholder code or TODOs unless requested.
- If you are unsure, explain the uncertainty instead of guessing.

Always prefer correctness, clarity, and maintainability over cleverness.
"""

AGENT_LIMIT = 20


def main(user_prompt: str, verbose: bool):
    _ = load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("no gemini api key configured in the environment")

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    client = genai.Client(api_key=api_key)

    for _ in range(AGENT_LIMIT):
        response = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=AVAILABLE_FUNCTIONS, system_instruction=SYSTEM_PROMPT
            ),
        )

        if not response.usage_metadata:
            raise RuntimeError("something went wrong with the request")

        if response.candidates:
            for candiate in response.candidates:
                if candiate.content:
                    messages.append(candiate.content)

        if verbose:
            print(f"User prompt: {user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        if response.text:
            print("Response:")
            print(response.text)

        function_call_results: list[types.Part] = []
        if response.function_calls:
            for function_call in response.function_calls:
                if verbose:
                    print(
                        f"Calling function: {function_call.name}({function_call.args})"
                    )
                else:
                    print(f" - Calling function: {function_call.name}")
                function_call_result = call_function(function_call)
                if not function_call_result.parts:
                    raise Exception("function call result does not have parts")
                if not function_call_result.parts[0].function_response:
                    raise Exception("expected first part to have function_response")
                function_call_results.append(function_call_result.parts[0])
                if verbose:
                    print(
                        f"-> {function_call_result.parts[0].function_response.response}"
                    )
        else:
            break
        messages.append(types.Content(role="user", parts=function_call_results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vibing")
    _ = parser.add_argument("user_prompt", type=str, help="User prompt")
    _ = parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()
    main(user_prompt=args.user_prompt, verbose=args.verbose)
