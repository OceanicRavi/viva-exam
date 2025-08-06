# viva-exam
# 🎓 Viva Exam System - Complete Setup Guide for Students

## Step 1: Check if Python is Already on Your Computer

1. **Press** `Windows key + R` on your keyboard
2. **Type** `cmd` and press Enter
3. A black window will open (this is called Command Prompt)
4. **Type** `python --version` and press Enter

**What you'll see:**
- ✅ If you see something like "Python 3.8.0" or "Python 3.9.0" → Python is installed! Go to Step 3
- ❌ If you see "python is not recognized" → You need to install Python. Go to Step 2

## Step 2: Install Python (if you don't have it)

1. **Open your web browser** (Chrome, Edge, Firefox)
2. **Go to:** `https://www.python.org/downloads/`
3. **Click** the big yellow "Download Python" button
4. **Wait** for the file to download (it's about 25MB)
5. **Find** the downloaded file (usually in your Downloads folder)
6. **Double-click** the file to run it
7. **⚠️ IMPORTANT:** Check the box that says "Add Python to PATH" at the bottom
8. **Click** "Install Now"
9. **Wait** for installation to complete (2-3 minutes)
10. **Click** "Close" when done

## Step 3: Download the Viva Exam Files

1. **Create a new folder** on your Desktop called "VivaExam"
2. **Download these 3 files** and put them in your VivaExam folder:
   - `main.py` (the main program)
   - `requirements.txt` (list of needed packages)
   - `audio_test.py` (to test your audio)

## Step 4: Get Your OpenAI API Key

1. **Go to:** `https://platform.openai.com/`
2. **Sign up** for a free account (you might need an adult to help)
3. **Go to** API Keys section
4. **Create** a new API key
5. **Copy** the key (it looks like: sk-proj-abc123...)
6. **Keep this safe** - you'll need it later

## Step 5: Install Required Packages

1. **Press** `Windows key + R`
2. **Type** `cmd` and press Enter
3. **Type** `cd Desktop\VivaExam` and press Enter
4. **Type** this command and press Enter:
   ```
   pip install openai PyPDF2 SpeechRecognition pyttsx3 pyaudio python-dotenv
   ```
5. **Wait** for everything to install (2-3 minutes)

**If you get an error about pyaudio:**
- **Type** this instead and press Enter:
  ```
  pip install pipwin
  pipwin install pyaudio
  pip install openai PyPDF2 SpeechRecognition pyttsx3 python-dotenv
  ```

## Step 6: Set Up Your API Key

1. **Open Notepad** (search for "Notepad" in Start menu)
2. **Type** this line, but replace "your-key-here" with your actual API key:
   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```
3. **Save the file** as `.env` (with the dot at the beginning)
4. **Make sure** to save it in your VivaExam folder
5. **Important:** When saving, change "Save as type" to "All Files" so it doesn't add .txt

## Step 7: Test Your Audio (Important!)

1. **Make sure** your microphone and speakers/headphones work
2. **Open Command Prompt** again (`Windows key + R`, type `cmd`)
3. **Type** `cd Desktop\VivaExam` and press Enter
4. **Type** `python audio_test.py` and press Enter
5. **Listen** for the test sounds
6. **If you hear all 3 test sounds** → Your audio works! ✅
7. **If you don't hear sounds** → Check your speakers/headphones

## Step 8: Prepare Your Study Material

1. **Get your study notes** in one of these formats:
   - PDF file (.pdf)
   - Text file (.txt)
2. **Put the file** in your VivaExam folder
3. **Remember the exact file name** (like "biology_notes.pdf")

## Step 9: Run the Viva Exam!

1. **Open Command Prompt** (`Windows key + R`, type `cmd`)
2. **Type** `cd Desktop\VivaExam` and press Enter
3. **Type** `python main.py` and press Enter
4. **Follow the instructions** on screen:
   - Enter your study file name (like "biology_notes.pdf")
   - Choose how many questions (1-6)
   - Answer the questions when asked!

## 🎤 During the Exam:

- **Speak clearly** into your microphone
- **Wait** for each question to be read aloud
- **Take your time** - you have 20 seconds to answer
- **Don't worry** if you get something wrong - it's for learning!

## 🆘 Troubleshooting:

**Problem:** "python is not recognized"
- **Solution:** Reinstall Python and make sure to check "Add Python to PATH"

**Problem:** Can't hear the questions
- **Solution:** Check your speakers, run `python audio_test.py` again

**Problem:** Microphone not working
- **Solution:** Check Windows microphone settings, make sure it's not muted

**Problem:** "OpenAI API error"
- **Solution:** Check your `.env` file has the correct API key

**Problem:** "File not found"
- **Solution:** Make sure your study file is in the VivaExam folder with the correct name

## 📁 Your VivaExam Folder Should Look Like This:
```
VivaExam/
├── main.py
├── audio_test.py
├── .env
├── your_study_notes.pdf (or .txt)
```

## 🎉 That's It!

You're ready to use the Viva Exam system! Remember:
- **Practice makes perfect** - try it multiple times
- **It's about learning** - don't worry about getting perfect scores
- **Have fun** with your studies!

Good luck with your viva exam! 🌟

----------------------------
pip uninstall openai PyPDF2 speechrecognition pyttsx3 pyaudio python-dotenv

pip install -r requirement.txt

pip uninstall pyaudio
pip install pipwin
pipwin install pyaudio==0.2.11