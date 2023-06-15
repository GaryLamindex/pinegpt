import openai
import os
import pandas as pd
from langchain.document_loaders import CSVLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import os

# def getIntent(api_key: str, user_message: str) -> str:
#     prompt = f"""
#     Please identify the intents of the following user inputs:

#     1. User: How much is the price of Apple stock?
#     AI: Intent: normal_chat

#     2. User: Can you provide the latest news on Tesla?
#     AI: Intent: normal_chat

#     3. User: What is the backtest result of the strategy?
#     AI: Intent: backtest_result_enquiry

#     4. User: what is the return between 2019 and 2020?
#     AI: Intent: backtest_result_enquiry

#     5. User: {user_message}
#     AI: Intent: """

#     openai.api_key = api_key

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "You are a helpful assistant that classifies user intents.",
#             },
#             {"role": "user", "content": prompt},
#         ],
#         temperature=0.5,
#     )

#     intent = response.choices[0].message['content'].strip().replace("assistant: ", "", 1)
#     return intent.lower()

# def read_backtest_csv(user_message):
    
#     loader = CSVLoader(file_path='backtest.csv')
#     # Create an index using the loaded documents
#     index_creator = VectorstoreIndexCreator()
#     docsearch = index_creator.from_loaders([loader])
#     chain = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.vectorstore.as_retriever(), input_key="question")
#     response = chain({"question": user_message})
#     print("backtest response:", response)

#     return response.get("result", "I couldn't find the information you're looking for.")


def create_chat_completion(api_key: str, messages: list) -> str:
    print("create_chat_completion")
    openai.api_key = api_key
    os.environ["OPENAI_API_KEY"] = api_key
    user_message = messages
    # user_message = messages[-1]['content']
    # intent = getIntent(api_key, user_message)
    # print("Intent:", intent)

    # if  'backtest_result_enquiry' in intent:
    #     csv_response = read_backtest_csv(user_message)
    #     return csv_response

    # print("Messages:", messages)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=user_message,
        temperature=0.5,
    )

    print("OpenAI response:", response)
    return response.choices[0].message['content'].strip().replace("assistant: ", "", 1)
