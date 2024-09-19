from flask import Flask, render_template, jsonify, request, url_for, send_file
from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Define the path to store the generated speech files on the Desktop
user_profile = os.path.expanduser('~')
desktop_path = Path(user_profile) / 'Desktop'
speech_file_path = desktop_path / 'speech.mp3'

# Ensure the folder exists (though not strictly necessary for Desktop path)
speech_file_path.parent.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    return render_template('tts-render-0918.html')

@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Generate the speech using OpenAI API
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )

        # Write the binary content of the audio file to the Desktop
        with open(speech_file_path, 'wb') as audio_file:
            audio_file.write(response.content)  # Write the binary content directly

        # Return the URL to the file
        file_url = url_for('download_speech', filename='speech.mp3', _external=True)
        return jsonify({"file_url": file_url}), 200

    except OpenAIError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-speech/<filename>')
def download_speech(filename):
    file_path = desktop_path / filename
    return send_file(file_path, as_attachment=True, mimetype='audio/mp3')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
