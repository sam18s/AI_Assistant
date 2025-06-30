from flask import Blueprint, render_template, jsonify, request
import speech_recognition as sr

# Define Blueprint
speech_bp = Blueprint(
    'speech',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/speech/static'
)

# Route: Page load
@speech_bp.route('/', methods=['GET'])
def speech_home():
    return render_template('speech/index.html')  # Make sure this path matches: templates/speech/index.html

# Route: Speech Recognition
@speech_bp.route('/recognize', methods=['POST'])
def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("🎤 Listening...")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"✅ Recognized: {text}")
            return jsonify({"success": True, "text": text})
    except sr.UnknownValueError:
        return jsonify({"success": False, "error": "Could not understand the audio."})
    except sr.RequestError as e:
        return jsonify({"success": False, "error": f"Speech recognition service error: {e}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
