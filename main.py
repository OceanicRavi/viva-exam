from openai import OpenAI
import PyPDF2
import speech_recognition as sr
import pyttsx3
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global TTS engine - initialize once
tts_engine = None

def init_tts():
    """Initialize TTS engine once"""
    global tts_engine
    try:
        tts_engine = pyttsx3.init()
        # Set properties
        tts_engine.setProperty('rate', 150)
        tts_engine.setProperty('volume', 0.95)
        
        # Try to set a good voice
        voices = tts_engine.getProperty('voices')
        if voices and len(voices) > 0:
            tts_engine.setProperty('voice', voices[0].id)
        
        return True
    except Exception as e:
        print(f"TTS initialization failed: {e}")
        return False

def speak_text(text):
    """Simple, reliable text-to-speech function"""
    global tts_engine
    
    print(f"🔊 {text}")
    
    # Try to reinitialize TTS if it's None
    if tts_engine is None:
        if not init_tts():
            print("(Audio unavailable - text only)")
            return
    
    try:
        # Clear any existing queue
        tts_engine.stop()
        
        # Speak the text
        tts_engine.say(text)
        tts_engine.runAndWait()
        
        # Small pause to ensure completion
        time.sleep(0.3)
        
    except Exception as e:
        print(f"Speech error: {e}")
        # Try to reinitialize
        try:
            tts_engine = pyttsx3.init()
            tts_engine.setProperty('rate', 150)
            tts_engine.setProperty('volume', 0.95)
            tts_engine.say(text)
            tts_engine.runAndWait()
            time.sleep(0.3)
        except:
            print("(Audio failed - continuing with text)")

def get_audio_input():
    """Get audio input from user"""
    recognizer = sr.Recognizer()
    
    speak_text("Please speak your answer now")
    
    try:
        with sr.Microphone() as source:
            print("🎤 Listening... (speak now)")
            
            # Adjust for noise briefly
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Listen for answer
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=20)
            
            print("Processing your answer...")
            answer = recognizer.recognize_google(audio)
            print(f"You said: {answer}")
            return answer
            
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.WaitTimeoutError:
        print("No audio detected")
        return None
    except Exception as e:
        print(f"Audio error: {e}")
        return None

def load_file(filepath):
    """Load content from PDF or TXT file"""
    try:
        if filepath.lower().endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + " "
                return text.strip()
        
        elif filepath.lower().endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            print("Use PDF or TXT files only")
            return None
            
    except Exception as e:
        print(f"File error: {e}")
        return None

def generate_questions(content, count):
    """Generate viva questions"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Create short, clear viva exam questions. Number them 1, 2, 3, etc."},
                {"role": "user", "content": f"Make {count} viva questions from this content:\n{content[:1200]}"}
            ],
            max_tokens=300
        )
        
        text = response.choices[0].message.content
        questions = []
        
        for line in text.split('\n'):
            line = line.strip()
            if line and any(char.isdigit() for char in line[:3]):
                # Remove number prefix
                if '. ' in line:
                    question = line.split('. ', 1)[1]
                elif ') ' in line:
                    question = line.split(') ', 1)[1]
                else:
                    question = line
                questions.append(question)
        
        return questions[:count]
        
    except Exception as e:
        print(f"Question generation error: {e}")
        return []

def get_feedback_and_score(question, answer):
    """Get detailed feedback with correct answer and scoring"""
    if not answer:
        return "That's okay! Moving on.", 0
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an encouraging teacher. Evaluate the student's answer and respond with:
                    1. Whether it's correct, partially correct, or incorrect (be gentle)
                    2. If wrong/incomplete, provide the correct answer briefly
                    3. Always end on a positive, encouraging note
                    4. Keep response under 40 words
                    5. Never be harsh or demotivating"""
                },
                {
                    "role": "user", 
                    "content": f"Question: {question}\nStudent Answer: {answer}\n\nEvaluate this answer and provide gentle feedback with the correct information if needed."
                }
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        feedback = response.choices[0].message.content.strip()
        
        # Simple scoring based on keywords in feedback
        feedback_lower = feedback.lower()
        if any(word in feedback_lower for word in ['correct', 'right', 'good', 'excellent', 'perfect']):
            score = 1
        elif any(word in feedback_lower for word in ['partially', 'somewhat', 'close', 'almost']):
            score = 0.5
        else:
            score = 0
            
        return feedback, score
        
    except Exception as e:
        return "Good effort! Keep going.", 0.5

def calculate_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return "A+ Excellent"
    elif percentage >= 80:
        return "A Good"
    elif percentage >= 70:
        return "B+ Well done"
    elif percentage >= 60:
        return "B Nice effort"
    elif percentage >= 50:
        return "C+ Keep improving"
    else:
        return "C Good try"

def main():
    """Main program"""
    print("🎓 VIVA EXAM SYSTEM")
    print("-" * 25)
    
    # Initialize TTS
    if init_tts():
        speak_text("Welcome to your viva exam!")
    else:
        print("🔊 Welcome to your viva exam! (Text-only mode)")
    
    # Get file
    filepath = input("📄 Enter file path (PDF/TXT): ").strip()
    content = load_file(filepath)
    
    if not content:
        speak_text("Could not load file. Please check the path.")
        return
    
    # Get question count
    try:
        count = int(input("❓ Number of questions (1-6): "))
        count = max(1, min(6, count))
    except:
        count = 3
    
    speak_text(f"I will ask {count} questions. Remember, this is about learning! Let's start!")
    
    # Generate questions
    questions = generate_questions(content, count)
    if not questions:
        speak_text("Could not create questions.")
        return
    
    time.sleep(1)
    
    # Ask questions and track score
    total_score = 0
    max_score = len(questions)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*40}")
        print(f"QUESTION {i}")
        print('='*40)
        print(question)
        
        # Ask question via audio
        speak_text(f"Question {i}. {question}")
        
        # Get answer
        answer = get_audio_input()
        
        # Get detailed feedback and score
        feedback, question_score = get_feedback_and_score(question, answer)
        total_score += question_score
        
        # Give feedback
        speak_text(feedback)
        
        # Pause between questions
        time.sleep(1.5)
    
    # Calculate final results
    percentage = (total_score / max_score) * 100
    grade = calculate_grade(percentage)
    
    # Final results
    print("\n🎉 EXAM COMPLETED!")
    print(f"📊 FINAL SCORE: {total_score:.1f}/{max_score} ({percentage:.0f}%)")
    print(f"🏆 GRADE: {grade}")
    
    # Verbal final score with encouragement
    if percentage >= 80:
        final_message = f"Fantastic! You scored {percentage:.0f} percent. Grade {grade}. You really know your material!"
    elif percentage >= 60:
        final_message = f"Well done! You scored {percentage:.0f} percent. Grade {grade}. You're doing great, keep studying!"
    else:
        final_message = f"Good effort! You scored {percentage:.0f} percent. Grade {grade}. Keep practicing and you'll improve!"
    
    speak_text(final_message)

if __name__ == "__main__":
    main()