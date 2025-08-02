from openai import OpenAI
import PyPDF2
import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv
load_dotenv()

# Set your OpenAI API key here
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========== AUDIO FUNCTIONS ==========

engine = pyttsx3.init()

def speak(text):
    print(f"🔊 AI says: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        try:
            audio = r.listen(source, timeout=5)
            response = r.recognize_google(audio)
            print(f"🗣️ You said: {response}")
            return response
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            speak("Sorry, I could not understand. Try again.")
            return None
        except sr.WaitTimeoutError:
            print("⏰ Timeout.")
            speak("No response detected. Try again.")
            return None

# ========== FILE LOADING ==========

def load_file_text(filepath):
    if filepath.endswith(".pdf"):
        import PyPDF2
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return " ".join([page.extract_text() for page in reader.pages])
    elif filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file format. Use PDF or TXT.")

# ========== AI FUNCTIONS ==========

def generate_questions(text, count):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're an examiner generating oral viva questions."},
            {"role": "user", "content": f"Generate {count} short viva-style questions based on this content:\n{text}"}
        ]
    )
    return response.choices[0].message.content.split('\n')

def score_answer(question, answer):
    prompt = f"This is a viva question: '{question}'. The student answered: '{answer}'. Give gentle, encouraging feedback. If correct, say it's good. If incorrect, explain simply."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a friendly and encouraging teacher."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ========== MAIN LOGIC ==========

def main():
    filepath = input("📄 Enter path to PDF or TXT file: ").strip()
    text = load_file_text(filepath)

    try:
        question_count = int(input("❓ How many questions to generate? "))
    except ValueError:
        question_count = 3
        print("⚠️ Invalid number, defaulting to 3 questions.")

    print("\n🤖 Generating viva questions...\n")
    questions = generate_questions(text, question_count)

    for i, q in enumerate(questions, 1):
        if not q.strip(): continue  # skip blanks
        print(f"❓ {i}. {q}")
        speak(f"Question {i}. {q}")

        attempts = 0
        user_answer = None
        while attempts < 3 and user_answer is None:
            user_answer = listen()
            attempts += 1

        if user_answer:
            feedback = score_answer(q, user_answer)
        else:
            feedback = "Let's skip this one and move to the next question."

        speak(feedback)
        print()

if __name__ == "__main__":
    main()