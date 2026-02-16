import cv2
import numpy as np
from database import *
from idantity import *
from audio import *
import time
from llm import *
import random

def main():
    init_db()
    cap = cv2.VideoCapture(0)
    UNKNOWN_COOLDOWN = 10
    KNOWN_COOLDOWN = 10
    active_user = {}
    unknown_conversation_count = 0
    ask_name_threshold = random.randint(3, 6)
    name_registered = False
    current_unknown_encoding = None

    active_user_id = None
    active_user_name = None
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb, locations = ditact_face(frame)
        encodings = face_encoding(rgb, locations)
      

        for encoding in encodings:
            user = match_face(encoding)
            if user is None:
                active_user_id = "unknown"
                active_user_name = "Guest"
                current_unknown_encoding = encoding
                temp_key ="unknown"
                if temp_key not in active_user or time.time() - active_user[temp_key] > UNKNOWN_COOLDOWN:
                    speak("Hello There")
                    active_user[temp_key] = time.time()
            else:
                user_id = user['id']
                name = user['name']
                active_user_id = user_id
                active_user_name = name                    
                if user_id not in active_user or time.time() - active_user[user_id] > KNOWN_COOLDOWN:
                        speak(f"well come back, {active_user_name}!")
                        active_user[user_id] = time.time()

        if active_user_id:
            record_until_silence()
            spoken_text = transcribe()
            if spoken_text:
                if active_user_id == "unknown":
                    unknown_conversation_count += 1
                    prompt = build_prompt(active_user_name, [], spoken_text)
                    speak(ask_llm(prompt))
                    if not name_registered and unknown_conversation_count >= ask_name_threshold:
                        speak("I don't know your name, can you please tell me?")
                        record_until_silence()
                        name_text = transcribe()
                        if name_text:
                            name = extract_name(name_text)
                            if name and current_unknown_encoding is not None:
                                new_id = add_user(name, current_unknown_encoding)
                                speak(f"Nice to meet you, {name}! I will remember you.")
                                active_user_id = new_id
                                active_user_name = name
                                name_registered = True
                else :
                    insert_conversation(active_user_id, "User:", spoken_text)
                    enforce_memmory_limit(active_user_id)
                    massages = load_last_conversations(active_user_id)
                    prompt = build_prompt(active_user_name, massages, spoken_text)
                    reply = ask_llm(prompt)
                    insert_conversation(active_user_id, "Luna", reply)
                    speak(reply)
        cv2.imshow("Luna AI", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    main()