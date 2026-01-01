import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

import config
import functions


def main(user_prompt: str, verbose: bool):
    _ = load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("no gemini api key configured in the environment")

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    client = genai.Client(api_key=api_key)

    for _ in range(config.AGENT_LIMIT):
        response = client.models.generate_content(
            model=config.MODEL,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=functions.AVAILABLE_FUNCTIONS,
                system_instruction=config.SYSTEM_PROMPT,
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
                function_call_result = functions.call_function(function_call)
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
