import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions import AVAILABLE_FUNCTIONS, call_function

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

AGENT_LIMIT = 10


def main(args: argparse.Namespace):
    _ = load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("no gemini api key configured in the environment")

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

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

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        if response.text:
            print("Response:")
            print(response.text)

        function_call_results: list[types.Part] = []
        if response.function_calls:
            for function_call in response.function_calls:
                if args.verbose:
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
                if args.verbose:
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
    main(args)
