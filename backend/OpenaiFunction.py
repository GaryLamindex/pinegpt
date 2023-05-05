import openai
import os
import pandas as pd

def getIntent(api_key: str, userInput: str) -> str:
    prompt = f"""
Please identify the intents of the following user inputs:

1. User: How much is the price of Apple stock?
   AI: Intent: normal_chat

2. User: Can you provide the latest news on Tesla?
   AI: Intent: normal_chat

3. User: What is the backtest result of the strategy?
   AI: Intent: strategy_backtest_result_enquiry

4. User: {userInput}
   AI: Intent: """

    openai.api_key = api_key

    response = openai.Completion.create(
        model='gpt-3.5-turbo',
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=["\n"],
    )

    intent = response.choices[0].text.strip()
    return intent

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
