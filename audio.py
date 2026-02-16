import re
import subprocess
import numpy as np
import sounddevice as sd
import wave 
import time 

WHISPER_BIN = "/home/user/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "/home/user/whisper.cpp/models/ggml-base.en.bin"

PIPER_BIN = "/home/user/piper/build/piper"
PIPER_VOICE = "/home/user/piper/voices/en_US-amy-medium.onnx"

AUDIO_IN = "input.wav"
AUDIO_OUT = "output.wav"

RATE = 16000
SILENCE_THRESHOLD = 500
MAX_SILENCE = 2.0


def speak(text):
    print(f"Speaking: {text}")
    p = subprocess.Popen([PIPER_BIN, "--model", PIPER_VOICE, "--output_file",  AUDIO_OUT],stdin=subprocess.PIPE)
    p.communicate(input=text.encode())

    subprocess.run(["aplay", AUDIO_OUT],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

def record_until_silence(filename=AUDIO_IN):

    frames = []
    silence_time = 0.0   
    start_time = time.time()

    try:
        with sd.InputStream(samplerate=RATE, channels=1, dtype="int16") as stream:

            while True:

                data, _ = stream.read(1024)
                frames.append(data)

                volume = np.abs(data).mean()

                if volume < SILENCE_THRESHOLD:
                    silence_time += 1024 / RATE
                    if silence_time >= MAX_SILENCE:
                        break
                else:
                    silence_time = 0.0

                if time.time() - start_time > 15:
                    break

    except Exception as e:
        print("Audio recording error:", e)
        return False

    if not frames:
        print("No audio captured.")
        return False

    try:
        audio = np.concatenate(frames)
    except Exception as e:
        print("Audio concatenate error:", e)
        return False

    try:
        with wave.open(filename, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(RATE)
            f.writeframes(audio.tobytes())
    except Exception as e:
        print("WAV write error:", e)
        return False

    return True


def transcribe(filename=AUDIO_IN):
    try :
        result = subprocess.check_output([
            WHISPER_BIN,
            "-m", WHISPER_MODEL,
            "-f", filename,
            "--language", "en",
            "--no-timestamps",
            "-t", "4",
            "--beam-size", "1"
        ])
        return result.decode().strip()
    except:
        return ""
    



def extract_name(text):
    if not text:
        return None

    text = text.strip()

    patterns = [
        r"\bmy name is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bmy name\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bi am\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bi'm\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bit is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bit's\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bcall me\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bpeople call me\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bthey call me\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bthe name is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bactually my name\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+here\b",
        r"\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+speaking\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()

            # Filter obvious non-name phrases
            if len(name.split()) > 5:
                continue

            return name.title()

    return text.strip().capitalize()
