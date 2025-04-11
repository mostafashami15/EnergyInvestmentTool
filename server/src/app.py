from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/api/analyze-input', methods=['POST'])
def analyze_input():
    user_input = request.json.get('userInput')
    
    # Call LLM API (example using OpenAI)
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system", 
                "content": "Extract the following parameters from user input: location, budget, and preferred energy types (if mentioned). Format as JSON."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                                headers=headers, json=data)
        response_data = response.json()
        return jsonify(response_data['choices'][0]['message']['content'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)