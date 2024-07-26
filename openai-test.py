from openai import OpenAI
import os
client = OpenAI(api_key="...")



completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "I want you to act as an SEO semantic core phrase generator.\nI want you to answer only with JSON array format, without any keys, just the array!\nDo not provide explanations.\n\nYou will be provided with a topic and keywords, and your task is to generate more than 100 low-frequency key phrases specific to that topic. \nEach phrase should contain between 4 to 12 words and be between 12 to 120 characters in length.I want you to act as a SEO semantic core phrase generator.\nI want you to answer only with JSON array format. No keys, just array!\nDo not provide explanations.\n\nYou will be provided with a topic and keywords, and your task is to generate 500 low-frequency key phrases only for that topic. \nIn each phrase must be from 4 to 12 words, and from 12 to 120 symbols."},
        {"role": "user", "content": "Topic: sporting goods.\nKeywords: male, female, children's, washing, cleaning, top, shows, fashion, jewelry, real estate, lawyers, medicine, health, travel, hotel.weights, dumbbells, trampolines, tents, massage tables, balls, exercise equipment, barbell, jump ropes, expander, boxing gloves"}
    ],
    max_tokens=3800,
    top_p=1,
    temperature=1,
    frequency_penalty=0.1,
    presence_penalty=0.1
)

print(completion.choices[0].message.content)
