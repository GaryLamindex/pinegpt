import openai
import os
import pandas as pd

def getIntent(api_key: str, user_message: str) -> str:
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that classifies user intents.",
            },
            {"role": "user", "content": user_message},
        ],
        temperature=0.5,
    )

    intent = response.choices[0].message['content'].strip().replace("assistant: ", "", 1)
    return intent.lower()


def handle_backtest_result_enquiry():
    df = pd.read_csv('backtest.csv')
    # Perform necessary calculations or extract relevant information from the CSV file
    answer = "Your backtest result summary: ...\n"
    return answer

def create_chat_completion(api_key: str, messages: list) -> str:
    openai.api_key = api_key

    user_message = messages[-1]['content']
    intent = getIntent(api_key, user_message)

    if intent == 'strategy_backtest_result_enquiry':
        backtest_answer = handle_backtest_result_enquiry()
        system_message = {'role': 'system', 'content': backtest_answer}
        messages.append(system_message)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.5,
    )

    print("OpenAI response:", response)
    return response.choices[0].message['content'].strip().replace("assistant: ", "", 1)
