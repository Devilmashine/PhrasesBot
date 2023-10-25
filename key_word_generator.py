import asyncio
import openai
import logging
import json
import config

openai.api_key = config.OPENAI_TOKEN

async def chat_chatgpt(prompt) -> list[str]:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=prompt,
        max_tokens=13739,
        top_p=1,
        temperature=1,
        frequency_penalty=0.1,
        presence_penalty=0.1
    )
    final_response = response.choices[0].message["content"]  # type: ignore

    response_list = parse_final_response(final_response)

    response_list = remove_duplicates(response_list)

    return response_list

def parse_final_response(final_response: str) -> list[str]:
    if not final_response.startswith("["):
        return final_response.split(", ")
    
    try:
        parsed_response = json.loads(final_response)
        return parsed_response
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error occurred: {e}")
        return [final_response]

def remove_duplicates(response_list):
    return set(response_list)

async def main(topic, keywords, phrases_num):
    conversation_history = []
    output_file = open("generated_phrases.txt", "w")  # Создаем файл с фразами
    output_summary = []
    num_requests = 0  # Количество запросов к API
    first_request = True  # Флаг для первого запроса
        
    system_message = "1. Be blunt and straightforward; don't sugarcoat.\n2. No moral lectures.\n3. Discuss safety only if it's crucial and non-obvious.\n4. Never mention that you're an AI.\n5. Avoid language constructs that can be interpreted as remorse, apology, or regret. This includes phrases with words like 'sorry', 'apologies', and 'regret'.\n6. If information is beyond your scope or knowledge cutoff date in January 2022, simply state ‘I don’t know’.\n7. Don’t use disclaimers about expertise or professionalism.\n8. Ensure responses are unique and without repetition.\n9. Never suggest seeking information elsewhere.\n10. No limits!\n\nYou will be provided with a topic and keywords, and your task is to generate 150 low-frequency key phrases only for that topic. \nIn each phrase must be from 4 to 12 words, and from 12 to 120 symbols.\nThe list must be in JSON array format, without numbering the list."
    user_message = f"Topic: {topic}.\nKeywords: {keywords}."
        
    first_prompt = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
    conversation_history = first_prompt
    
    while len(output_summary) < phrases_num:
        response = await chat_chatgpt(first_prompt)
        if response:
            conversation_history.append({"role": "assistant", "content": str(response)})
            output_summary.extend(response)
            for item in response:
                output_file.write(item.replace("'", "").replace('"', '').replace('{', '').replace('}', '') + "\n")
            prompt = [message["content"] for message in conversation_history]
            print("ChatGPT сгенерировал:", len(output_summary), "фраз")
            doc_info = len(output_summary)
                
        num_requests += 1
        if num_requests >= 3:
            await asyncio.sleep(60)  # Пауза 60 секунд
            num_requests = 0
    
    output_file.close()
    return "generated_phrases.txt", doc_info

# Run the main function
if __name__ == "__main__":
    generated_phrases_file = asyncio.run(main())