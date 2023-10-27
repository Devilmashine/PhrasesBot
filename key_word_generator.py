import asyncio
import time
import openai
import logging
import json
import config

openai.api_key = config.OPENAI_TOKEN

async def main(prompt) -> list[str]:
    """Generates a list of phrases from a given prompt using the ChatGPT language model."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=prompt,
            max_tokens=7000,
            top_p=1,
            temperature=1,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        final_response = response.choices[0].message["content"]  # type: ignore

        response_list = parse_final_response(final_response)

        response_list = remove_duplicates(response_list)

        return response_list
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return []

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
    generated_phrases_file = asyncio.run(main())