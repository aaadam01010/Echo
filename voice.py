import asyncio
import edge_tts
import ctypes
import time
import os
import threading

def play_mp3_windows(file_path):
    """Plays an MP3 file using Windows native media engine (No pygame needed)."""
    # Open the MP3 file natively
    err = ctypes.windll.winmm.mciSendStringW(f'open "{file_path}" alias echo_audio type mpegvideo', None, 0, None)
    if err == 0:
        # Play the file
        ctypes.windll.winmm.mciSendStringW('play echo_audio', None, 0, None)
        
        # Wait until she finishes speaking
        while True:
            status = ctypes.create_unicode_buffer(256)
            ctypes.windll.winmm.mciSendStringW('status echo_audio mode', status, 256, None)
            if status.value != 'playing':
                break
            time.sleep(0.1)
            
        # Close the file
        ctypes.windll.winmm.mciSendStringW('close echo_audio', None, 0, None)

async def _generate_and_play(text, voice):
    try:
        # Clean text to prevent playback errors
        clean_text = text.replace('"', '').replace("'", "").replace("\n", " ")
        
        # Generate speech using the highly natural Edge Neural voice
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save("temp_echo.mp3")
        
        # Play it if it exists
        if os.path.exists("temp_echo.mp3"):
            play_mp3_windows("temp_echo.mp3")
            os.remove("temp_echo.mp3") # Clean up the temp file
                
    except Exception as e:
        print(f"Voice error: {e}")

def speak(text):
    """Makes Echo speak with a natural, human voice."""
    print(f"️ Echo says: {text}")
    
    # VOICE SELECTION:
    # "en-US-AriaNeural" -> Very natural, expressive, human-like female voice.
    voice = "en-US-AriaNeural" 
    
    # Run in a background thread so the UI never freezes
    threading.Thread(target=lambda: asyncio.run(_generate_and_play(text, voice)), daemon=True).start()