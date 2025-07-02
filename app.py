from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import threading
import requests
import random
import os
import re
import wikipedia
import pyjokes
# import pywhatkit
import subprocess
import platform
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from geopy.geocoders import Nominatim
from PyDictionary import PyDictionary
import webbrowser
# import pyautogui
from googletrans import Translator
import webbrowser
import urllib.parse
# from transformers import pipeline
from pdf_converter.routes import pdf_bp
from speech_recog.routes import speech_bp 

# Load once at the start
# generator = pipeline("text-generation", model="gpt2")


# Initialize Flask app
app = Flask(__name__)

# Load secrets from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

dictionary = PyDictionary()
translator = Translator()

# # Email configuration (replace with your email credentials)
# EMAIL_ADDRESS = "your_email@example.com"
# EMAIL_PASSWORD = "your_email_password"

def speak(text):
    """Simultaneously speak and print the given text."""
    if text:
        print(text)  # Print immediately

        def speaks():
            try:
                # Initialize the pyttsx3 engine
                engine = pyttsx3.init('sapi5')
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[1].id)  # Use male voice
                engine.say(text)
                engine.runAndWait()
                engine.stop()  # Properly stop the engine
            except Exception as e:
                print(f"Error: {e}. Could not speak the text.")

        # Run the speak function in a separate thread
        speak_thread = threading.Thread(target=speaks)
        speak_thread.start()

# Function to take voice command
def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you repeat?")
        except sr.RequestError as e:
            speak("Sorry, my speech service is down.")

def get_weather(city):
    """Fetches weather information for a given city using OpenWeatherMap API."""
    api_key = "fc3380c0294c5688f37a2a395cad0e76"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            return f"The weather in {city.title()} is {weather_desc} with a temperature of {temp}°C and humidity of {humidity}%."
        elif response.status_code == 404:
            return f"City '{city}' not found. Please check the city name and try again."
        else:
            return "Unable to fetch weather details at the moment. Please try again later."
    except Exception as e:
        return f"An error occurred: {str(e)}. Unable to fetch weather details."

def get_news(query=None):
    api_key = "abe0b7347adb4be7a92e0e12c0bcc8ca"
    if query:
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"
    else:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    try:
        response = requests.get(url)
        news_data = response.json()
        if news_data["status"] == "ok":
            articles = news_data["articles"][:5]  # Get top 5 articles
            news = "\n".join([f"{i+1}. {article['title']}" for i, article in enumerate(articles)])
            return news
        else:
            return "Unable to fetch news."
    except Exception:
        return "Unable to fetch news at the moment."

def get_random_advice():
    advice_list = [
        "Always be kind to others.",
        "Take breaks when working for long hours.",
        "Learn something new every day.",
        "Stay hydrated and drink plenty of water.",
        "Believe in yourself and your abilities.",
        "Focus on progress, not perfection.",
        "Surround yourself with positive people.",
        "Practice gratitude daily.",
        "Don't be afraid to ask for help.",
        "Take care of your mental health.",
    ]
    return random.choice(advice_list)

def calculate_math(expression):
    try:
        # Allow only valid characters: digits, operators, parentheses, and spaces
        if re.match(r'^[\d\s+\-*/().]+$', expression):
            # Evaluate the expression safely
            result = eval(expression)
            return f"The result is {result}."
        else:
            return "Invalid mathematical expression."
    except Exception as e:
        return "Sorry, I couldn't calculate that."

def search_youtube(query):
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Searching YouTube for {query}."

def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching Google for {query}."

def close_program(program_name):
    try:
        os.system(f"taskkill /f /im {program_name}")
        return f"Closed {program_name}."
    except Exception as e:
        return f"Sorry, I couldn't close {program_name}."
    
# def play_music_on_youtube():
#     speak("Which song do you want to play?")
#     song = take_command()
#     if song:
#         speak(f"Playing {song} on YouTube.")
#         pywhatkit.playonyt(song)
#         return f"Playing {song} on YouTube."
#     else:
#         return "Sorry, I didn't catch the song name."

def play_music_on_youtube():
    speak("Which song do you want to play?")
    song = take_command()
    if song:
        speak(f"Opening YouTube search for {song}.")
        # Open YouTube search in browser instead of playing directly
        webbrowser.open(f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}")
        return f"Searching YouTube for {song}."
    else:
        return "Sorry, I didn't catch the song name."
    
def check_internet_speed():
    webbrowser.open("https://www.speedtest.net/")
    return "Opening Speedtest to check your internet speed."

# def chat_with_huggingface(prompt):
#     try:
#         response = generator(prompt, max_length=100, num_return_sequences=1)
#         return response[0]['generated_text']
#     except Exception as e:
#         return f"HuggingFace Error: {str(e)}"


def set_alarm(alarm_time):
    def alarm():
        while True:
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == alarm_time:
                speak("Time's up! Alarm ringing.")
                break
            time.sleep(10)

    threading.Thread(target=alarm).start()
    return f"Alarm set for {alarm_time}."

def set_reminder(reminder_text, reminder_time):
    def reminder():
        while True:
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == reminder_time:
                speak(f"Reminder: {reminder_text}")
                break
            time.sleep(10)

    threading.Thread(target=reminder).start()
    return f"Reminder set for {reminder_time}."

def get_system_info():
    system_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Processor": platform.processor(),
        "Architecture": platform.machine(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
    }
    return system_info

def convert_currency(amount, from_currency, to_currency):
    api_key = "56e01d8ca77d7875cd8276ef"  # Replace with your API key
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    try:
        response = requests.get(url)
        data = response.json()
        rate = data['rates'][to_currency]
        converted_amount = amount * rate
        return f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}."
    except Exception as e:
        return "Sorry, I couldn't convert the currency."

# def send_email(to, subject, body):
#     try:
#         msg = MIMEMultipart()
#         msg['From'] = EMAIL_ADDRESS
#         msg['To'] = to
#         msg['Subject'] = subject
#         msg.attach(MIMEText(body, 'plain'))
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#         server.sendmail(EMAIL_ADDRESS, to, msg.as_string())
#         server.quit()
#         return "Email sent successfully."
#     except Exception as e:
#         return f"Failed to send email: {e}"

def search_nearby_places(place_type, location):
    geolocator = Nominatim(user_agent="assistant")
    location = geolocator.geocode(location)
    if location:
        latitude, longitude = location.latitude, location.longitude
        return f"Searching for {place_type} near {location.address}."
    else:
        return "Sorry, I couldn't find the location."
    

# from nltk.corpus import wordnet
# import nltk
# nltk.download('wordnet')

# def get_word_meaning(word):
#     """
#     Get the first meaning of a word using WordNet.
#     """
#     try:
#         synsets = wordnet.synsets(word)
#         if synsets:
#             definition = synsets[0].definition()
#             return f"{word.capitalize()} means: {definition}"
#         else:
#             return f"Sorry, I couldn't find the meaning of '{word}'."
#     except Exception as e:
#         return f"Error while looking up the word: {str(e)}"



def get_word_synonyms(word):
    synonyms = dictionary.synonym(word)
    if synonyms:
        return synonyms
    else:
        return "Sorry, I couldn't find synonyms for that word."

def get_word_antonyms(word):
    antonyms = dictionary.antonym(word)
    if antonyms:
        return antonyms
    else:
        return "Sorry, I couldn't find antonyms for that word."



# ------------------ Database Model ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 

with app.app_context():
    db.create_all()


# Dictionary of apps to open
open_apps = {
    "calculator": (r"C:\Windows\System32\calc.exe", "Opening Calculator."),
    "notepad": (r"C:\Windows\System32\notepad.exe", "Opening Notepad."),
    "camera": ("start microsoft.windows.camera:", "Opening Camera."),
    "setting": ("start ms-settings:", "Opening Windows Settings."),
    "file manager": ("explorer", "Opening File Explorer."),
    "explorer": ("explorer", "Opening File Explorer."),
    "command prompt": ("cmd", "Opening Command Prompt."),
    "cmd": ("cmd", "Opening Command Prompt."),
    "control panel": ("control", "Opening Control Panel."),
    "paint": ("mspaint", "Opening Paint."),
    "media player": ("wmplayer", "Opening Windows Media Player."),
    "excel": ("excel", "Opening Microsoft Excel."),
    "word": ("winword", "Opening Microsoft Word."),
}

# Define app close commands in a dictionary
close_apps = {
    "vs code": ("Code.exe", "Visual Studio Code closed."),
    "calculator": ("calc.exe", "Calculator closed."),
    "notepad": ("notepad.exe", "Notepad closed."),
    "camera": ("WindowsCamera.exe", "Camera closed."),  # might not always work
    "setting": ("SystemSettings.exe", "Settings closed."),  # fallback name
    # "file manager": ("explorer.exe", "File Manager closed."),
    # "explorer": ("explorer.exe", "File Manager closed."),
    "command prompt": ("cmd.exe", "Command Prompt closed."),
    "cmd": ("cmd.exe", "Command Prompt closed."),
    "control panel": ("control.exe", "Control Panel closed."),
    "paint": ("mspaint.exe", "Paint closed."),
    "media player": ("wmplayer.exe", "Windows Media Player closed."),
    "excel": ("excel.exe", "Microsoft Excel closed."),
    "word": ("winword.exe", "Microsoft Word closed."),
}


# Register Blueprints
app.register_blueprint(pdf_bp, url_prefix='/pdf')
app.register_blueprint(speech_bp, url_prefix='/speech')


# ------------------ Routes ------------------

@app.route('/')
def home():
    if 'user_id' in session:
        speak("Hello! I am Lucy AI, a highly intelligent virtual assistant designed to efficiently perform various tasks and provide seamless assistance. How may I help you?")
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


# ------------------ AI Assistant Logic ------------------

@app.route('/execute_command', methods=['POST'])
def execute_command():
    data = request.json
    text = data.get('text', '').lower()
    ai_response = ""

    if "how are you" in text or "kaise ho" in text:
        ai_response = "I am absolutely fine. What about you?"
    
    # elif "ask with ai" in text:
    #     query = text.replace("ask with ai", "").strip()

    #     if query:
    #         speak(f"Asking AI: {query}")

    #         # Open ChatGPT in browser
    #         webbrowser.open("https://chat.openai.com/chat")

    #         # Wait for browser to load completely (adjust if needed)
    #         time.sleep(8)

    #         # Type the query and press Enter
    #         pyautogui.write(query, interval=0.05)
    #         pyautogui.press("enter")

    #         speak("Your query has been automatically typed into ChatGPT.")
    #     else:
    #         speak("You said 'ask with AI', but didn't specify your question. Please say the full query.")


    elif "ask with ai" in text:
        query = text.replace("ask with ai", "").strip()
        if query:
            speak(f"Asking AI: {query}")
            # Just open ChatGPT without automation
            webbrowser.open(f"https://chat.openai.com/?q={query}")
            speak("I've opened ChatGPT in your browser. You can now ask your question there.")
        else:
            speak("You said 'ask with AI', but didn't specify your question. Please say the full query.")

    # Open VS Code
    elif "open vs code" in text:
        code_path = r"C:\Users\Samiksha\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        if os.path.exists(code_path):
            subprocess.Popen([code_path])
            ai_response = "Opening Visual Studio Code."
        else:
            ai_response = "I couldn't find Visual Studio Code at the specified location."

    
    # Check if text contains "open {something}"
    elif any(f"open {key}" in text for key in open_apps):
        for app_key, (app_path, message) in open_apps.items():
            if f"open {app_key}" in text:
                # Use subprocess for .exe and commands; use os.system for shell calls
                if app_path.startswith("start"):
                    os.system(app_path)
                elif os.path.exists(app_path) or "\\" in app_path: 
                    subprocess.Popen([app_path])
                else:
                    subprocess.Popen(app_path)  
                ai_response = message
                break


    elif "open" in text:
        # Dictionary of common websites
        site_urls = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "manipal university": "https://student.onlinemanipal.com/s/",
        "github": "https://github.com",
        "chatgpt": "https://chat.openai.com",
        "linkdin" : "https://www.linkedin.com/"
        }

        site_name = text.replace("open", "").strip()

        if site_name in site_urls:
            webbrowser.open(site_urls[site_name])
            ai_response = f"Opening {site_name}..."
        else:
            # Try searching the site name on Google
            search_url = f"https://www.google.com/search?q={site_name}"
            webbrowser.open(search_url)
            ai_response = f"I couldn't find a direct link for {site_name}, so I searched it on Google."

    # Check if user said "close" followed by app name
    elif any(f"close {key}" in text for key in close_apps):
        for app_name, (process, message) in close_apps.items():
            if f"close {app_name}" in text:
                os.system(f"taskkill /f /im {process}")
                ai_response = message
                break

    # Close Calculator
    elif "close calculator" in text:
        os.system("taskkill /f /im calc.exe")
        ai_response = "Calculator closed."

    elif "close everything" in text:
        closed = []
        for _, (process_name, message) in close_apps.items():
            result = os.system(f"taskkill /f /im {process_name} >nul 2>&1")
            if result == 0:
                closed.append(message)

        if closed:
            ai_response = "I closed the following applications:\n" + "\n".join(closed)
        else:
            ai_response = "There were no apps to close or they were already closed."

    elif 'time' in text:
        current_time = datetime.now().strftime("%I:%M %p")
        ai_response = f"The current time is {current_time}."
        
    elif 'date' in text or 'day' in text:
        current_date = datetime.now().strftime("%A, %d %B %Y")
        ai_response = f"Today is {current_date}."

    elif "search on youtube" in text:
        query = text.replace("search on youtube", "").strip()
        if query:
            ai_response = search_youtube(query)

    elif "search on google" in text:
        query = text.replace("search on google", "").strip()
        if query:
            ai_response = search_google(query)

    elif 'weather' in text:
        city_match = re.search(r'weather(?: in)? (.+)', text)
        if city_match:
            city = city_match.group(1).strip()
            ai_response = get_weather(city)
        else:
            ai_response = "Please specify a city for the weather details."
    
    elif "who invented you" in text:
        ai_response = "I was created by Samiksha"

    elif "what is your name" in text:
        ai_response = "my name is lucy."

    elif "thank you" in text or "thanks" in text:
        ai_response = "You're welcome!"

    elif "bye" in text:
        ai_response = "Goodbye! Have a great day ahead."

    elif "good morning" in text:
        ai_response = "Good morning! I hope you have a productive day 😊"

    elif "nice to meet you" in text:
        ai_response = "Nice to meet you too! 😊 How can I help you today?"
    
    elif "i am fine" in text:
        ai_response = "Good 😊 How can I help you today?"

    elif "good night" in text:
        ai_response = "Good night! Sweet dreams 🌙"

    elif "hello" in text or "hi" in text:
        ai_response = "Hello! How can I assist you today?"

    elif "love you" in text:
        ai_response = "Aww, thank you! I'm always here for you ❤️"

    elif "who are you" in text:
        ai_response = "I’m your personal AI assistant created by Samiksha!"

    elif 'news' in text:
        topic = text.replace('news about', '').strip()
        ai_response = get_news(topic)

    elif 'advice' in text:
        ai_response = get_random_advice()

    elif 'calculate' in text:
        expression = text.replace('calculate', '').strip()
        ai_response = calculate_math(expression)

    elif 'wikipedia' in text:
        query = text.replace('search on wikipedia', '').strip()
        try:
            results = wikipedia.summary(query, sentences=10)
            ai_response = results
        except Exception:
            ai_response = "Sorry, I couldn't find anything on Wikipedia."

    elif 'joke' in text:
        ai_response = pyjokes.get_joke()
    
    # # Take Screenshot
    # elif "take screenshot" in text or "screenshot" in text:
    #     try:
    #         # Get path to Downloads folder
    #         downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            
    #         timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #         filename = f"screenshot_{timestamp}.png"
    #         screenshot_path = os.path.join(downloads_path, filename)

    #         # Take and save screenshot
    #         screenshot = pyautogui.screenshot()
    #         screenshot.save(screenshot_path)

    #         # Optional: Open the screenshot after saving
    #         os.startfile(screenshot_path)

    #         ai_response = f"Screenshot saved in Downloads as {filename}."
    #     except Exception as e:
    #         ai_response = f"Failed to take screenshot: {str(e)}"

    elif "play music on youtube" in text:
        ai_response = play_music_on_youtube()

    elif "check internet speed" in text:
        ai_response = check_internet_speed()

    elif "translate" in text:
        try:
            # Sample input: "translate how are you to hindi"
            parts = text.split("to")
            if len(parts) == 2:
                sentence = parts[0].replace("translate", "").strip()
                target_lang = parts[1].strip().lower()

                lang_codes = {
                    "hindi": "hi", "english": "en", "marathi": "mr",
                    "french": "fr", "spanish": "es", "german": "de",
                    "telugu": "te", "tamil": "ta", "gujarati": "gu",
                    "japanese": "ja", "chinese": "zh-cn"
                }

                if target_lang in lang_codes:
                    translated = translator.translate(sentence, dest=lang_codes[target_lang])
                    ai_response = f"'{sentence}' in {target_lang.capitalize()} is: '{translated.text}'"
                else:
                    ai_response = f"Sorry, I don't support the language '{target_lang}' yet."
            else:
                ai_response = "Please say something like: translate how are you to Hindi."
        except Exception as e:
            ai_response = f"Translation error: {str(e)}"


    elif "set alarm" in text:
        ai_response = "What time should I set the alarm?"
        alarm_time = take_command()
        ai_response = set_alarm(alarm_time)

    elif "set reminder" in text:
        ai_response = "What should I remind you about?"
        reminder_text = take_command()
        ai_response = "When should I remind you?"
        reminder_time = take_command()
        ai_response = set_reminder(reminder_text, reminder_time)

    elif "system information" in text:
        system_info = get_system_info()
        ai_response = "Here is your system information:\n" + "\n".join([f"{key}: {value}" for key, value in system_info.items()])

    elif "convert currency" in text:
        ai_response = "How much do you want to convert?"
        amount = float(take_command())
        ai_response = "From which currency?"
        from_currency = take_command().upper()
        ai_response = "To which currency?"
        to_currency = take_command().upper()
        ai_response = convert_currency(amount, from_currency, to_currency)

    # elif "send email" in text:
    #     ai_response = "To whom should I send the email?"
    #     to = input("Enter recipient's email: ").strip()
    #     ai_response = "What is the subject?"
    #     subject = take_command()
    #     ai_response = "What should I write in the email?"
    #     body = take_command()
    #     ai_response = send_email(to, subject, body)
    
    elif "nearby" in text or "find" in text or "location" in text:
        try:
            # Handle phrases like "find hospital", "nearby petrol pump", etc.
            query = ""
            if "nearby" in text:
                query = text.split("nearby")[-1].strip()
            elif "find" in text:
                query = text.split("find")[-1].strip()
            elif "location" in text:
                query = text.split("find")[-1].strip()

            if query:
                search_query = urllib.parse.quote(query + " near me")
                maps_url = f"https://www.google.com/maps/search/{search_query}"
                webbrowser.open(maps_url)
                ai_response = f"Searching for {query} near you..."
            else:
                ai_response = "Please specify what you're looking for nearby."

        except Exception as e:
            ai_response = f"Sorry, I couldn't search maps: {str(e)}"


    # elif "meaning of" in text or "define" in text or "what is" in text:
    #     # Extract the word from the spoken sentence
    #     word = ""
    #     if "meaning of" in text:
    #         word = text.split("meaning of")[-1].strip()
    #     elif "define" in text:
    #         word = text.split("define")[-1].strip()
    #     elif "what is" in text:
    #         word = text.split("what is")[-1].strip()

    #     ai_response = get_word_meaning(word)


    elif "synonyms of" in text:
        word = text.replace("synonyms of", "").strip()
        ai_response = get_word_synonyms(word)

    elif "antonyms of" in text:
        word = text.replace("antonyms of", "").strip()
        ai_response = get_word_antonyms(word)

    elif "search" in text or "who is" in text or "what is" in text:
        query = text.replace("search", "").replace("who is", "").replace("what is", "").strip()
        ai_response = f"Searching Google for {query}"
        webbrowser.open(f"https://www.google.com/search?q={query}")
        
    # elif 'lucy' in text or 'ai question' in text:
    #     prompt = text.replace("ask ai", "").replace("ai question", "").strip()
    #     if prompt:
    #         ai_response = chat_with_huggingface(prompt)
    #     else:
    #         ai_response = "Please provide a full question to ask AI."


    print(f"AI Response: {ai_response}")
    speak(ai_response)
    return jsonify({"user_input": text, "ai_response": ai_response}), 200

if __name__ == '__main__':
    app.run(debug=True)  

