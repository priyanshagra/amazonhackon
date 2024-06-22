import os
from flask import Flask, request, jsonify, send_from_directory
from google.cloud import speech
from transformers import pipeline
import soundfile as sf
import numpy as np
from TTS.api import TTS
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize the Coqui TTS models
coqui_tts_model_1 = TTS("tts_models/en/ljspeech/tacotron2-DDC")
coqui_tts_model_2 = TTS("tts_models/en/ljspeech/glow-tts")

# Initialize other pipelines
speech_client = speech.SpeechClient()
language_detector = pipeline("language-detection")
sentiment_analyzer = pipeline("sentiment-analysis")
llm_model = pipeline("text-generation", model="gpt-2")  # Change to "facebook/llama2" if needed

def process_audio(audio_data):
    # Convert audio to text using Google Speech-to-Text
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US"
    )
    response = speech_client.recognize(config=config, audio=audio)
    text = response.results[0].alternatives[0].transcript

    # Detect language and sentiment of text
    language = language_detector(text)[0]["language"]
    sentiment = sentiment_analyzer(text)[0]["label"]

    # Create prompt template for LLM
    prompt_template = f"Respond in {language} with a {sentiment} tone: "
    prompt = prompt_template + text

    # Generate response from LLM
    llm_response = llm_model(prompt, max_length=100)

    # Convert response to speech using TTS models
    response_text = llm_response[0]["generated_text"]
    coqui_audio_1 = coqui_tts_model_1.tts_to_file(text=response_text, file_path="static/coqui_output_1.wav")
    coqui_audio_2 = coqui_tts_model_2.tts_to_file(text=response_text, file_path="static/coqui_output_2.wav")

    # Return TTS output file paths
    return "static/coqui_output_1.wav", "static/coqui_output_2.wav"

@app.route('/process_audio', methods=['POST'])
def process_audio_route():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    audio_data = audio_file.read()

    try:
        coqui_audio_1, coqui_audio_2 = process_audio(audio_data)

        # Send the TTS outputs back to the frontend
        return jsonify({
            "coqui_audio_1": coqui_audio_1,
            "coqui_audio_2": coqui_audio_2
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)

