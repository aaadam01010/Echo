import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import os

def record_audio(filename="temp_record.wav", duration=8, fs=44100): # INCREASED TO 8 SECONDS
    print("🎤 Listening...")
    try:
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        wav.write(filename, fs, audio_data)
        return filename
    except Exception as e:
        print(f"❌ Mic error: {e}")
        return None

def listen_and_transcribe() -> str:
    audio_file = record_audio(duration=8)
    if not audio_file or not os.path.exists(audio_file):
        return ""

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"👂 Raw Heard: {text}")
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"❌ Speech service error: {e}")
        return ""
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

def should_respond_to(text: str) -> bool:
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # 1. WAKE WORDS (Catches misheard "Echo")
    wake_variations = [
        "echo", "hey echo", "hello echo", "eco", "eko", "echou"
    ]
    for wake in wake_variations:
        if wake in text_lower:
            return True
            
    # 2. GARBAGE FILTER (Ignores background noise like "Oklahoma Lottery")
    # If it's less than 4 words and has no question mark, it's probably background noise.
    if len(text.split()) < 4 and "?" not in text:
        return False

    # 3. DIRECT QUESTIONS (Short, clear questions directed at her)
    if len(text.split()) < 10 and "?" in text:
        return True
        
    return False