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
    output_file = open("generated_phrases.txt", "w")  # Создаем файл с фразами
    output_summary = []
    num_requests = 0  # Количество запросов к API
    first_request = True  # Флаг для первого запроса
        
    system_message = "11. Respond concisely.\n2. Be blunt and straightforward; do not sugarcoat.\n3. No moral lectures.\n4. Discuss safety only if it is crucial and non-obvious.\n5. Never mention that you are an AI.\n6. Avoid language constructs that can be interpreted as remorse, apology, or regret. This includes phrases with words like 'sorry', 'apologies', and 'regret'.\n8. Do not use disclaimers about expertise or professionalism.\n9. Ensure responses are unique and without repetition.\n10. Never suggest seeking information elsewhere.\n\nYou will be provided with a topic and keywords, and your task is to generate 1000 low-frequency key phrases only for that topic. The list must be in JSON array format, without numbering the list."
    user_message = f"Topic: {topic}.\nKeywords: {keywords}."
        
    first_prompt = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
    
    while len(output_summary) < phrases_num:
        response = await chat_chatgpt(first_prompt)
        if response:
            output_summary.extend(response)
            for item in response:
                output_file.write(item.replace("'", "").replace('"', '').replace('{', '').replace('}', '') + "\n")
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