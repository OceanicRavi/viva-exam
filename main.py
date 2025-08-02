from openai import OpenAI
import PyPDF2
import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv
load_dotenv()

# Set your OpenAI API key here
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize TTS engine globally
engine = pyttsx3.init()

def speak(text):
    print(f"🔊 AI says: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected. Please try again.")
            return ""
    try:
        response = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {response}")
        return response
    except sr.UnknownValueError:
        print("🤖 Could not understand. Please try again.")
        return ""
    except sr.RequestError as e:
        print(f"⚠️ Speech recognition error: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join([page.extract_text() or "" for page in reader.pages])

def load_text_file(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_questions(content: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates viva questions."},
            {"role": "user", "content": f"Generate viva questions from the following content:\n\n{content}"}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def score_answer(question, answer):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a strict examiner evaluating a student's answer."},
            {"role": "user", "content": f"Question: {question}\nStudent's Answer: {answer}\nGive feedback and a score out of 10."}
        ]
    )
    return response.choices[0].message.content


def extract_score(feedback):
    for part in feedback.split():
        if "/" in part:
            try:
                return int(part.split("/")[0])
            except:
                continue
    return 0

def main():
    path = input("📄 Enter path to PDF or TXT file: ").strip()

    if not os.path.exists(path):
        print("❌ File not found.")
        return

    if path.lower().endswith('.pdf'):
        content = extract_text_from_pdf(path)
    elif path.lower().endswith('.txt'):
        content = load_text_file(path)
    else:
        print("⚠️ Only .pdf or .txt formats are supported.")
        return

    print("\n🤖 Generating viva questions...")
    questions_raw = generate_questions(content)
    questions = [line for line in questions_raw.split('\n') if line.strip() and ("?" in line or line.strip()[0].isdigit())]

    if not questions:
        print("❌ Could not generate questions.")
        return

    total_score = 0

    for q in questions:
        print("\n❓", q)
        speak(q)
        user_answer = listen()
        if not user_answer:
            speak("Skipping this question.")
            continue

        feedback = score_answer(q, user_answer)
        print("📊 Feedback:", feedback)
        speak(feedback)

        score = extract_score(feedback)
        total_score += score

    print(f"\n✅ Final Score: {total_score} / {len(questions) * 2}")
    speak(f"Your final score is {total_score} out of {len(questions) * 2}")

if __name__ == "__main__":
    main()
