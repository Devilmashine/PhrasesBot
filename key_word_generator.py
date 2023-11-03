import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
import time
import openai
import logging
import json

load_dotenv(dotenv_path=".env")
OPENAI_TOKENS = os.getenv("OPENAI_TOKENS")
keys = OPENAI_TOKENS.split(",") # Set of API keys like ["key1", "key2", "key3"] (os.getenv("OPENAI_TOKENS"))
print(keys)

async def generate_phrases(prompt, api_key) -> list[str]:
    """Generates a list of phrases from a given prompt using the ChatGPT language model."""
    try:
        start_time = time.monotonic()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=prompt,
            max_tokens=7000,
            top_p=1,
            temperature=1,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            api_key=api_key  # Use the current API key
        )
        final_response = response.choices[0].message["content"]  # type: ignore

        response_list = await asyncio.to_thread(parse_final_response, final_response)

        response_list = remove_duplicates(response_list)
        end_time = time.monotonic()
        iteration_time = end_time - start_time
        if iteration_time < 20:
            await asyncio.to_thread(time.sleep, iteration_time)  # Pause between requests
        return response_list
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return []

async def main(prompt):
    """Runs the main function with multiple prompts in parallel using multiple API keys."""

    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        results = await asyncio.gather(
            *[loop.run_in_executor(executor, generate_phrases, prompt, api_key) for api_key in keys]
        )

    generated_phrases = []
    for result in results:
        generated_phrases.extend(await result)  # Await the coroutine

    return generated_phrases


def parse_final_response(final_response: str) -> list[str]:
    """Parses the final response from the ChatGPT language model into a list of phrases."""

    if not final_response.startswith("["):
        return final_response.split(", ")
    
    try:
        parsed_response = json.loads(final_response)
        return parsed_response
    except (json.JSONDecodeError, AttributeError) as e:
        logging.error(f"Error occurred: {e}")
        return [final_response]

def remove_duplicates(response_list):
    """Removes duplicates from a list of phrases."""

    return set(response_list)


# Run the main function
if __name__ == "__main__":
    generated_phrases = asyncio.run(main())