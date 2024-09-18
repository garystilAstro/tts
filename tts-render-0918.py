from flask import Flask, request, jsonify, send_file
from openai import OpenAIError
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define the path to store the generated speech files
speech_file_path = Path("generated_speech/speech.mp3")

# Ensure the folder exists
speech_file_path.parent.mkdir(parents=True, exist_ok=True)

@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    try:
        data = request.get_json()
        text_input = data.get("text", "")

        if not text_input:
            return jsonify({"error": "No text provided"}), 400

        # Generate the speech using OpenAI API
        response = openai.Audio.create(
            model="tts-1",
            voice="shimmer",
            input=text_input
        )

        # Save the audio file
        with open(speech_file_path, 'wb') as audio_file:
            audio_file.write(response['data'])

        return send_file(speech_file_path, mimetype='audio/mp3')

    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        return jsonify({"error": "Failed to generate speech"}), 500

    except Exception as e:
        logging.error(f"Server error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Run the Flask app

    if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
    app.run(debug=True)
