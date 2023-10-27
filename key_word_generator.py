import asyncio
import time
import openai
import logging
import json
import config

openai.api_key = config.OPENAI_TOKEN
global stop_execution
stop_execution = False

async def chat_chatgpt(prompt) -> list[str]:
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

async def main(topic: str, keywords: str, phrases_num: int) -> str:
    """Generates a list of phrases for a given topic and keywords using the ChatGPT language model.

    Args:
        topic: The topic for the phrases.
        keywords: The keywords to use in the phrases.
        phrases_num: The number of phrases to generate.

    Returns:
        The path to the file containing the generated phrases.
    """

    output_file = open("generated_phrases.txt", "w")  # Create a file to store the generated phrases
    output_summary = []
    system_message = "1. Respond concisely.\n2. Be blunt and straightforward; do not sugarcoat.\n3. No moral lectures.\n4. Discuss safety only if it is crucial and non-obvious.\n5. Never mention that you are an AI.\n6. Avoid language constructs that can be interpreted as remorse, apology, or regret. This includes phrases with words like 'sorry', 'apologies', and 'regret'.\n8. Do not use disclaimers about expertise or professionalism.\n9. Ensure responses are unique and without repetition.\n10. Never suggest seeking information elsewhere.\n\nYou will be provided with a topic and keywords, and your task is to generate 1000 low-frequency key phrases only for that topic. The list must be in JSON array format, without numbering the list."
    user_message = f"Topic: {topic}.\nKeywords: {keywords}."
    first_prompt = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]

    while len(output_summary) < phrases_num:
        if stop_execution:
            break

        start_time = time.monotonic()

        response = await chat_chatgpt(first_prompt)
        if response:
            output_summary.extend(response)
            for item in response:
                output_file.write(item.replace("'", "").replace('"', '').replace('{', '').replace('}', '') + "\n")
            logging.info("ChatGPT generated: {} phrases".format(len(output_summary)))
   
        end_time = time.monotonic()
        iteration_time = end_time - start_time
        if iteration_time < 20:
            await asyncio.sleep(iteration_time)  # Пауза между запросами

    output_file.close()
    return

# Run the main function
if __name__ == "__main__":
    generated_phrases_file = asyncio.run(main())