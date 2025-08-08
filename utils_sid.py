from openai import OpenAI
import os

openai_api = os.getenv('open_ai_api')
model = "gpt-4o-mini"

data_dir = "../data"
regulations_dir = [os.path.join(data_dir, entry) for entry in os.listdir(data_dir)if os.path.isdir(os.path.join(data_dir, entry))]
regulations_file = "../data/regulation.json"

def make_prompt(system_message, user_message):
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

def ask_ai(prompt, standard_output=None):
    client = OpenAI(api_key=openai_api)
    if standard_output:
        completion = client.chat.completions.create(model=model,messages=prompt,temperature=0, response_format={'type': 'list'})
    completion = client.chat.completions.create(model=model,messages=prompt,temperature=0)
    result = completion.choices[0].message.content
    return result
