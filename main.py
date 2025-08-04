from openai import OpenAI
import PyPDF2
import speech_recognition as sr
import pyttsx3
import os
import time
from dotenv import load_dotenv
import atexit

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global TTS engine - initialize once and reuse
tts_engine = None
tts_available = False

def cleanup_tts():
    """Cleanup function for program exit"""
    global tts_engine
    try:
        if tts_engine:
            tts_engine.stop()
            del tts_engine
    except (NameError, AttributeError):
        # tts_engine was never initialized or already cleaned up
        pass
    except Exception:
        # Any other cleanup error
        pass

# Register cleanup function
atexit.register(cleanup_tts)

def init_tts():
    """Initialize TTS engine once with better error handling"""
    global tts_engine, tts_available
    
    if tts_engine is not None:
        return tts_available
    
    try:
        tts_engine = pyttsx3.init()
        
        # Test if engine works
        voices = tts_engine.getProperty('voices')
        if not voices:
            raise Exception("No voices available")
        
        # Set properties
        tts_engine.setProperty('rate', 150)
        tts_engine.setProperty('volume', 0.95)
        
        # Use first available voice
        tts_engine.setProperty('voice', voices[0].id)
        
        tts_available = True
        print("🔊 Audio system initialized successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Audio system unavailable: {e}")
        print("📝 Continuing in text-only mode")
        tts_available = False
        tts_engine = None
        return False

def speak_text(text):
    """Improved text-to-speech function with better error handling"""
    global tts_engine, tts_available
    
    print(f"🔊 {text}")
    
    if not tts_available:
        return
    
    # Reinitialize if needed
    if tts_engine is None:
        if not init_tts():
            return
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # Clear any existing queue
            tts_engine.stop()
            
            # Speak the text
            tts_engine.say(text)
            tts_engine.runAndWait()
            
            # Ensure completion
            time.sleep(0.2)
            return
            
        except Exception as e:
            print(f"Speech attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                # Try to reinitialize
                try:
                    cleanup_tts()
                    time.sleep(0.5)
                    init_tts()
                except:
                    pass
            else:
                print("(Audio failed - continuing with text)")
                tts_available = False

def get_text_input():
    """Get text input from user - much more reliable than audio!"""
    
    speak_text("Please type your answer. Take your time to give a complete response.")
    print("💡 Type your answer below - you can take as long as you need!")
    print("💡 Press Enter when you're finished with your answer.")
    print("💡 For longer answers, you can type multiple sentences.")
    
    try:
        print("\n" + "="*50)
        print("✏️  TYPE YOUR ANSWER:")
        answer = input("Your answer: ").strip()
        
        if answer:
            print(f"✅ You answered: '{answer}'")
            return answer
        else:
            print("❌ No answer provided")
            return None
            
    except KeyboardInterrupt:
        print("\n❌ Input cancelled")
        return None
    except Exception as e:
        print(f"❌ Input error: {e}")
        return None

def load_file(filepath):
    """Load content from PDF or TXT file with better error handling"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    
    try:
        if filepath.lower().endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if len(reader.pages) == 0:
                    print("PDF file appears to be empty")
                    return None
                
                text = ""
                for page_num, page in enumerate(reader.pages):
                    try:
                        text += page.extract_text() + " "
                    except Exception as e:
                        print(f"Warning: Could not read page {page_num + 1}: {e}")
                
                return text.strip() if text.strip() else None
        
        elif filepath.lower().endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return content if content else None
        else:
            print("Please use PDF or TXT files only")
            return None
            
    except PermissionError:
        print(f"Permission denied accessing file: {filepath}")
        return None
    except Exception as e:
        print(f"File reading error: {e}")
        return None

def generate_questions(content, count):
    """Generate viva questions with better error handling"""
    if not content:
        return []
    
    try:
        # Truncate content if too long
        content_sample = content[:1500] if len(content) > 1500 else content
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Create clear, concise viva exam questions. Number them 1, 2, 3, etc. Each question should be specific and answerable."},
                {"role": "user", "content": f"Create exactly {count} viva questions from this content:\n{content_sample}"}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        text = response.choices[0].message.content
        questions = []
        
        for line in text.split('\n'):
            line = line.strip()
            if line and any(char.isdigit() for char in line[:5]):
                # Remove number prefix more robustly
                for separator in ['. ', ') ', ': ', '- ']:
                    if separator in line:
                        parts = line.split(separator, 1)
                        if len(parts) > 1:
                            question = parts[1].strip()
                            if question:
                                questions.append(question)
                                break
        
        # Ensure we have the right number of questions
        questions = questions[:count]
        
        if len(questions) < count:
            print(f"Warning: Only generated {len(questions)} questions instead of {count}")
        
        return questions
        
    except Exception as e:
        print(f"Question generation error: {e}")
        return []

def get_feedback_and_score(question, answer):
    """FIXED: Get detailed feedback with PROPER scoring"""
    if not answer or not answer.strip():
        return "No answer provided. Let's move on to the next question.", 0
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a viva exam evaluator. Your response must follow this EXACT format:
                    
                    SCORE: [0 for incorrect, 0.5 for partially correct, 1 for correct]
                    FEEDBACK: [Your encouraging feedback explaining the correct answer]
                    
                    Be strict but fair in scoring:
                    - SCORE: 1 only if the answer is substantially correct
                    - SCORE: 0.5 if the answer has some correct elements but misses key points
                    - SCORE: 0 if the answer is wrong or completely off-topic
                    
                    Always provide the correct answer in your feedback."""
                },
                {
                    "role": "user", 
                    "content": f"Question: {question}\nStudent Answer: {answer}\n\nEvaluate this answer and provide a score and feedback."
                }
            ],
            max_tokens=200,
            temperature=0.1  # Lower temperature for more consistent scoring
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse the response to extract score and feedback
        score = 0
        feedback = "Good effort! Keep learning."
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('SCORE:'):
                try:
                    score_text = line.replace('SCORE:', '').strip()
                    score = float(score_text)
                    # Ensure score is valid
                    if score not in [0, 0.5, 1]:
                        score = 0
                except:
                    score = 0
            elif line.startswith('FEEDBACK:'):
                feedback = line.replace('FEEDBACK:', '').strip()
        
        # If no proper format found, fallback to keyword analysis
        if 'SCORE:' not in response_text:
            response_lower = response_text.lower()
            if any(word in response_lower for word in ['correct', 'right', 'exactly', 'perfect']):
                score = 1
            elif any(word in response_lower for word in ['partially', 'somewhat', 'partly', 'close']):
                score = 0.5
            else:
                score = 0
            feedback = response_text
            
        return feedback, score
        
    except Exception as e:
        print(f"Feedback generation error: {e}")
        return "Could not generate feedback. Moving on.", 0

def calculate_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return "A+ Outstanding"
    elif percentage >= 80:
        return "A Excellent"
    elif percentage >= 70:
        return "B+ Good Work"
    elif percentage >= 60:
        return "B Nice Effort"
    elif percentage >= 50:
        return "C+ Keep Improving"
    else:
        return "C Needs More Study"

def main():
    """Main program with improved timing and scoring"""
    print("🎓 VIVA EXAM SYSTEM")
    print("-" * 30)
    
    # Initialize TTS
    init_tts()
    speak_text("Welcome to your viva exam system!")
    
    # Get file
    while True:
        filepath = input("📄 Enter file path (PDF/TXT): ").strip().strip('"')
        content = load_file(filepath)
        
        if content:
            print(f"✅ File loaded successfully ({len(content)} characters)")
            break
        else:
            print("❌ Could not load file. Please try again.")
            retry = input("Try another file? (y/n): ").lower()
            if retry != 'y':
                return
    
    # Get question count
    while True:
        try:
            count = int(input("❓ Number of questions (1-10): "))
            count = max(1, min(10, count))
            break
        except ValueError:
            print("Please enter a valid number")
    
    speak_text(f"I will ask you {count} questions. I'll read each question aloud, then you can type your answer. Take your time to give detailed responses!")
    
    # Generate questions
    print("🤔 Generating questions...")
    questions = generate_questions(content, count)
    
    if not questions:
        speak_text("Sorry, I couldn't create questions from this content.")
        return
    
    print(f"✅ Generated {len(questions)} questions")
    time.sleep(2)
    
    # Ask questions and track score
    total_score = 0
    max_score = len(questions)
    question_scores = []  # Track individual scores for debugging
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"QUESTION {i} of {len(questions)}")
        print('='*60)
        print(question)
        print("⏱️  You have 45 seconds to answer")
        
        # Ask question via audio, get typed answer
        speak_text(f"Question {i}. {question}")
        
        # Get typed answer instead of audio
        answer = get_text_input()
        
        # Get detailed feedback and score
        feedback, question_score = get_feedback_and_score(question, answer)
        total_score += question_score
        question_scores.append(question_score)
        
        # Show the score clearly
        print(f"\n📊 QUESTION {i} RESULT:")
        print(f"Your Answer: {answer if answer else 'No answer'}")
        print(f"Score: {question_score}/1")
        print(f"Feedback: {feedback}")
        
        # Give feedback
        speak_text(f"You scored {question_score} out of 1. {feedback}")
        
        # Show running total
        current_percentage = (total_score / i) * 100
        print(f"📈 Running Score: {total_score}/{i} ({current_percentage:.1f}%)")
        
        # Pause between questions
        if i < len(questions):
            print("\n⏳ Next question coming up...")
            time.sleep(3)
    
    # Calculate final results
    percentage = (total_score / max_score) * 100
    grade = calculate_grade(percentage)
    
    # Final results with detailed breakdown
    print("\n" + "🎉" * 25)
    print("EXAM COMPLETED!")
    print("🎉" * 25)
    
    # Show individual question scores
    print("\n📊 DETAILED RESULTS:")
    for i, score in enumerate(question_scores, 1):
        print(f"Question {i}: {score}/1")
    
    print(f"\n🏆 FINAL SCORE: {total_score:.1f}/{max_score} ({percentage:.1f}%)")
    print(f"📜 GRADE: {grade}")
    
    # Encouraging final message based on actual performance
    if percentage >= 80:
        final_message = f"Excellent work! You scored {percentage:.1f} percent with grade {grade}. You really understand this material!"
    elif percentage >= 60:
        final_message = f"Well done! You scored {percentage:.1f} percent with grade {grade}. You're making good progress!"
    elif percentage >= 40:
        final_message = f"Good effort! You scored {percentage:.1f} percent with grade {grade}. Keep studying to improve further!"
    else:
        final_message = f"You scored {percentage:.1f} percent with grade {grade}. Don't worry - practice more and you'll definitely improve!"
    
    speak_text(final_message)
    print(f"\n💬 {final_message}")
    
    # Study suggestions
    if percentage < 70:
        print(f"\n💡 STUDY TIP: Review the material and try the exam again to improve your score!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exam interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your setup and try again.")
    finally:
        cleanup_tts()