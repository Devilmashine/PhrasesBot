import asyncio
import openai
import time
import json

api_key = "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" 
openai.api_key = api_key 

import json

async def chat_chatgpt_stream(prompt) -> list[str]:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=prompt,
        max_tokens=10000,
        top_p=1,
        stop=None,
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
        return final_response[1:-1].split(", ")
    try:
        return json.loads(final_response)
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error occurred: {e}")
        return [final_response]


def remove_duplicates(response_list: list[str]) -> list[str]:
    return list(set(response_list))

async def main(topic, keywords, phrases_num):
    conversation_history = []
    output_file = open("generated_phrases.txt", "w")  # Создаем файл с фразами
    output_summary = []
    num_requests = 0  # Количество запросов к API
    first_request = True  # Флаг для первого запроса
        
    system_message = "1. Respond concisely.\n2. Be blunt and straightforward; don't sugarcoat.\n3. No moral lectures.\n4. Discuss safety only if it's crucial and non-obvious.\n5. Never mention that you're an AI.\n6. Avoid language constructs that can be interpreted as remorse, apology, or regret. This includes phrases with words like 'sorry', 'apologies', and 'regret'.\n7. If information is beyond your scope or knowledge cutoff date in January 2022, simply state ‘I don’t know’.\n8. Don’t use disclaimers about expertise or professionalism.\n9. Ensure responses are unique and without repetition.\n10. Never suggest seeking information elsewhere.\n\nYou will be provided with a topic and keywords, and your task is to generate 1000 low-frequency key phrases only for that topic. \nIn each phrase must be from 4 to 12 words, and from 12 to 120 symbols/\nThe list must be in JSON array format, without numbering the list."
    user_message = f"Topic: {topic}.\nSeed words: {keywords}."
        
    conversation_history = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
        
    prompt = conversation_history
        
    while len(output_summary) < phrases_num:
        if first_request:
            response = await chat_chatgpt_stream(prompt)
            first_request = False
        else:
            conversation_history.append({"role": "user", "content": "please continue!"})
            prompt = conversation_history
            response = await chat_chatgpt_stream(prompt)
            
        if response:
            conversation_history.append({"role": "assistant", "content": str(response)})
            output_summary.extend(response)
            for item in response:
                output_file.write(item.replace("'", "").replace('"', '') + "\n")
                
            prompt = [message["content"] for message in conversation_history]
                
            print("ChatGPT сгенерировал:", len(output_summary), "фраз")
                
        num_requests += 1
        if num_requests >= 3:
            time.sleep(60)  # Пауза 60 секунд
            num_requests = 0
    
    output_file.close()
    return "generated_phrases.txt"

# Run the main function
if __name__ == "__main__":
    generated_phrases_file = asyncio.run(main("clothes", "male, female, children's, washing, cleaning, top, shows, fashion, jewelry, real estate, lawyers, medicine, health, travel, hotel", 100))
    print(f"Generated phrases saved in {generated_phrases_file}")