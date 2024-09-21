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
    return render_template('tts-render-0921.html')

@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    data = request.json
    text = data.get('text', '')
    model = data.get('model', 'tts-1')  # Default model
    voice = data.get('voice', 'alloy')  # Default voice
    output_format = data.get('output_format', 'mp3')  # Default output format

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Generate the speech using OpenAI API with selected options
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        # Save the file in the selected output format (e.g., mp3)
        speech_file_path_with_format = speech_file_path.with_suffix(f'.{output_format}')
        with open(speech_file_path_with_format, 'wb') as audio_file:
            audio_file.write(response.content)  # Write the binary content

        file_url = url_for('download_speech', filename=f'speech.{output_format}', _external=True)
        return jsonify({"file_url": file_url}), 200

    except OpenAIError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-speech/<filename>')
def download_speech(filename):
    file_path = desktop_path / filename
    return send_file(file_path, as_attachment=True, mimetype=f'audio/{filename.split(".")[-1]}')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))

