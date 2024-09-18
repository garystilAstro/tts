from flask import Flask, request, jsonify, send_file, url_for, render_template
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
speech_file_directory = Path("generated_speech")
speech_file_directory.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    return render_template('tts-render-0918.html')

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
        file_name = "speech.mp3"
        speech_file_path = speech_file_directory / file_name
        with open(speech_file_path, 'wb') as audio_file:
            audio_file.write(response['data'])

        # Return the URL to the file
        file_url = url_for('download_speech', filename=file_name, _external=True)
        return jsonify({"file_url": file_url}), 200

    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        return jsonify({"error": "Failed to generate speech"}), 500

    except Exception as e:
        logging.error(f"Server error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/download-speech/<filename>')
def download_speech(filename):
    speech_file_path = speech_file_directory / filename
    return send_file(speech_file_path, as_attachment=True)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
