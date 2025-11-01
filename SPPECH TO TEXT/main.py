from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import os
from googletrans import Translator

app = Flask(__name__)

# Language mapping
LANGUAGE_MAP = {
    'english': 'en-US',
    'hindi': 'hi-IN',
    'telugu': 'te-IN',
    'tamil': 'ta-IN',
    'kannada': 'kn-IN'
}

# Initialize translator
translator = Translator()

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    selected_language = "english"  # default language
    translated_text = ""
    
    if request.method == "POST":
        selected_language = request.form.get("language", "english")
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                print(f"Listening in {selected_language}...")
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                recognizer.pause_threshold = 1  # seconds of non-speaking audio before a phrase is considered complete
                
                print("Speak now...")
                audio_clip = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                
                try:
                    language_code = LANGUAGE_MAP.get(selected_language, 'en-US')
                    transcript = recognizer.recognize_google(audio_clip, language=language_code)
                    print(f"Recognized: {transcript}")
                    
                    # Translate to English if not already in English
                    if selected_language != 'english' and transcript:
                        try:
                            translated = translator.translate(transcript, dest='en')
                            translated_text = translated.text
                        except Exception as e:
                            translated_text = f"Translation error: {str(e)}"
                    
                except sr.UnknownValueError:
                    transcript = "Could not understand the audio. Please try again."
                except sr.RequestError as e:
                    transcript = f"Error with speech recognition service: {str(e)}"
                except sr.WaitTimeoutError:
                    transcript = "No speech detected. Please try again."
                    
        except Exception as e:
            transcript = f"Error accessing microphone: {str(e)}"
    
    return render_template("index.html", 
                         transcript=transcript, 
                         translated_text=translated_text,
                         selected_language=selected_language,
                         languages=LANGUAGE_MAP.keys())

@app.route("/api/recognize", methods=["POST"])
def api_recognize():
    """API endpoint for AJAX requests"""
    try:
        data = request.get_json()
        selected_language = data.get('language', 'english')
        
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.1)
            recognizer.pause_threshold = 0.5
            
            print(f"API Listening in {selected_language}...")
            audio_clip = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            language_code = LANGUAGE_MAP.get(selected_language, 'en-US')
            transcript = recognizer.recognize_google(audio_clip, language=language_code)
            
            # Translate to English if not already in English
            translated_text = ""
            if selected_language != 'english' and transcript:
                try:
                    translated = translator.translate(transcript, dest='en')
                    translated_text = translated.text
                except Exception as e:
                    translated_text = f"Translation error: {str(e)}"
            
            return jsonify({
                'success': True,
                'transcript': transcript,
                'translated_text': translated_text,
                'language': selected_language
            })
            
    except sr.UnknownValueError:
        return jsonify({
            'success': False,
            'error': 'Could not understand the audio. Please try again.'
        })
    except sr.RequestError as e:
        return jsonify({
            'success': False,
            'error': f'Error with speech recognition service: {str(e)}'
        })
    except sr.WaitTimeoutError:
        return jsonify({
            'success': False,
            'error': 'No speech detected. Please try again.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        })

@app.route("/api/translate", methods=["POST"])
def api_translate():
    """API endpoint for translating existing text"""
    try:
        data = request.get_json()
        text_to_translate = data.get('text', '')
        source_language = data.get('source_language', 'auto')
        
        if not text_to_translate:
            return jsonify({
                'success': False,
                'error': 'No text provided for translation'
            })
        
        # Translate to English
        translated = translator.translate(text_to_translate, src=source_language, dest='en')
        
        return jsonify({
            'success': True,
            'original_text': text_to_translate,
            'translated_text': translated.text,
            'source_language': translated.src
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Translation error: {str(e)}'
        })

if __name__ == "__main__":
    app.run(debug=True)