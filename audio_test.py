import pyttsx3
import time
import sys

def cleanup_engine(engine):
    """Properly cleanup TTS engine"""
    try:
        if engine:
            engine.stop()
            # Small delay to ensure cleanup
            time.sleep(0.2)
            del engine
    except:
        pass

def test_basic_tts():
    """Test 1: Basic TTS with proper cleanup"""
    print("Test 1: Basic TTS")
    engine = None
    try:
        engine = pyttsx3.init()
        engine.say("Test one")
        engine.runAndWait()
        print("✅ Test 1 passed")
        return True
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    finally:
        cleanup_engine(engine)

def test_multiple_calls():
    """Test 2: Multiple calls with proper resource management"""
    print("Test 2: Multiple calls")
    engine = None
    try:
        engine = pyttsx3.init()
        
        # Set properties
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # First call
        engine.say("Test two")
        engine.runAndWait()
        time.sleep(0.5)
        
        # Second call - reuse same engine
        engine.say("Test three")
        engine.runAndWait()
        
        print("✅ Test 2 passed")
        return True
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False
    finally:
        cleanup_engine(engine)

def test_voices():
    """Test 3: Available voices"""
    print("Test 3: Available voices")
    engine = None
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"Found {len(voices)} voices:")
        for i, voice in enumerate(voices):
            print(f"  {i}: {voice.name}")
        print("✅ Test 3 passed")
        return True
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False
    finally:
        cleanup_engine(engine)

def test_single_engine_multiple_calls():
    """Test 4: Single engine for multiple calls (recommended approach)"""
    print("Test 4: Single engine multiple calls")
    engine = None
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        test_phrases = ["Test four", "Test five", "Test six"]
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"  Speaking phrase {i}...")
            engine.say(phrase)
            engine.runAndWait()
            time.sleep(0.3)  # Small pause between phrases
        
        print("✅ Test 4 passed")
        return True
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    finally:
        cleanup_engine(engine)

def main():
    print("🔊 Audio System Test")
    print("=" * 30)
    
    # System info
    print(f"Python version: {sys.version}")
    try:
        import pyttsx3
        print(f"pyttsx3 available: Yes")
    except ImportError:
        print(f"pyttsx3 available: No")
        return
    
    print("\nRunning tests...\n")
    
    # Run all tests
    tests = [
        test_basic_tts,
        test_multiple_calls, 
        test_voices,
        test_single_engine_multiple_calls
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Pause between tests
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All audio tests successful!")
    else:
        print("⚠️  Some tests failed - check system audio configuration")

if __name__ == "__main__":
    main()