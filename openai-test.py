from openai import OpenAI
import os
client = OpenAI(api_key="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")



completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": "I want you to act as an SEO semantic core phrase generator.\nI want you to answer only with JSON array format, without any keys, just the array!\nDo not provide explanations.\n\nYou will be provided with a topic and keywords, and your task is to generate more than 100 low-frequency key phrases specific to that topic. \nEach phrase should contain between 4 to 12 words and be between 12 to 120 characters in length."},
        {"role": "user", "content": "Topic: clothes.\nKeywords: male, female, children's, washing, cleaning, top, shows, fashion, jewelry, real estate, lawyers, medicine, health, travel, hotel."}
    ],
    max_tokens=3800,
    top_p=1,
    temperature=1,
    frequency_penalty=0.1,
    presence_penalty=0.1
)

print(completion.choices[0].message.content)