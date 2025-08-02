import pyttsx3
import time

# Test 1: Basic TTS
print("Test 1: Basic TTS")
try:
    engine = pyttsx3.init()
    engine.say("Test one")
    engine.runAndWait()
    print("✅ Test 1 passed")
except Exception as e:
    print(f"❌ Test 1 failed: {e}")

time.sleep(1)

# Test 2: Multiple calls
print("Test 2: Multiple calls")
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    
    engine.say("Test two")
    engine.runAndWait()
    time.sleep(0.5)
    
    engine.say("Test three")
    engine.runAndWait()
    print("✅ Test 2 passed")
except Exception as e:
    print(f"❌ Test 2 failed: {e}")

# Test 3: Check available voices
print("Test 3: Available voices")
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print(f"Found {len(voices)} voices:")
    for i, voice in enumerate(voices):
        print(f"  {i}: {voice.name}")
    print("✅ Test 3 passed")
except Exception as e:
    print(f"❌ Test 3 failed: {e}")