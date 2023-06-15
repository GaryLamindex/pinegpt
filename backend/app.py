from flask import Flask, jsonify, send_file
from flask_cors import CORS
from OpenaiFunction import create_chat_completion
import os
import csv
from flask import Flask, request
from algo.accelerating_dual_momentum.realtime import realtime
from datetime import datetime as dt
from pathlib import Path
from ongoing_signal_application import OngoingSignalApplication
import pandas as pd
import json

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


@app.route('/api/tables', methods=['GET'])
def get_all_tables():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(script_dir, "..", "user_id_0", "ongoing", "database.json")
    
    with open(database_path, 'r') as json_file:
        database = json.load(json_file)
    
    return jsonify(database)


@app.route('/api/<table_id>/data', methods=['GET'])
def get_all_data(table_id):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(script_dir, "..", "user_id_0", "ongoing", "database.json")
    
    with open(database_path, 'r') as json_file:
        database = json.load(json_file)
        folder_name = next((item["folder_name"] for item in database if item["table_id"] == int(table_id)), None)
        print("table_id::",table_id)
        print("folder_name::",folder_name)

    folder_path = os.path.join(script_dir, "..", "user_id_0", "ongoing", folder_name)
    
    stats_csv_path = os.path.join(folder_path, 'stats_data', "all_file_return.csv")
    drawdown_csv_path = os.path.join(folder_path, 'stats_data', "drawdown_abstract.csv")
    run_data_csv_path = os.path.join(folder_path, 'run_data', f"{folder_name}.csv")
    info_data_csv_path = os.path.join(folder_path, 'info_data.json')
    
    stats_data = pd.read_csv(stats_csv_path).to_json(orient='records')
    drawdown_data = pd.read_csv(drawdown_csv_path).to_json(orient='records')
    run_data = pd.read_csv(run_data_csv_path).to_json(orient='records')
    # Read the info_data.txt as a text file, not a csv file
    with open(info_data_csv_path, 'r') as file:
        info_data = file.read()
    
    return jsonify({
        'stats_data': json.loads(stats_data),
        'drawdown_data': json.loads(drawdown_data),
        'run_data': json.loads(run_data),
        'info_data': info_data,
    })

# create an instance of OngoingSignalApplication
signal_app = OngoingSignalApplication()

@app.route('/restart', methods=['POST'])
def restart():
    # call the restart() function
    print("Restarting backtests...")
    signal_app.restart()

    return jsonify({"message": "Backtests restarted."}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=5000)


# self.table_name = str(self.get_next_table_name()) + "__" + self.table_info.get("strategy_name") 
# self.table_path = f"{self.path}/{self.table_name}"


# def get_next_table_name(self):
#     try:
#         existing_tables = [int(dir_name) for dir_name in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, dir_name)) and dir_name.isdigit()]
#         if existing_tables:
#             return max(existing_tables) + 1
#         else:
#             return 0
#     except FileNotFoundError:
#         return 0