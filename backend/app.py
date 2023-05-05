from flask import Flask, request, jsonify
from flask_cors import CORS
from OpenaiFunction import create_chat_completion

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    # Process the data and generate a response
    message_history = data['messageHistory']
    current_message = data['currentMessage']
    user_message = current_message['content']
    api_key = data['apiKey']

    # Combine message_history and current_message for OpenAI prompt
    messages = message_history + [current_message]

    print("Chat history:", message_history)
    print("Current message:", current_message)
    print("Prompt:", messages)

    # Call the create_chat_completion function from openai_function.py
    assistant_message = create_chat_completion(api_key, messages)

    print("Assistant message:", assistant_message)

    response = {
        'choices': [
            {
                'message': {
                    'content': assistant_message
                }
            }
        ]
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
